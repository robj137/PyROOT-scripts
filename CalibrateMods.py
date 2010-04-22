#!/usr/bin/python

import math
import ROOT
import sys
import os


ROOT.gApplication.ExecuteFile("~/rootlogon.C")

def getMCASumHist(fileName, datasetName):
  x_min = 0
  x_max = 65536
  histo = ROOT.TH1D(datasetName,"", 65536,x_min,x_max)
  file = ROOT.TFile.Open(fileName)
  list = file.GetListOfKeys()
  size = list.GetSize()
  print 'number of keys: ' + str(size)
  for i in range(0,size):
    histo.Add(file.Get(list.At(i).GetName()))
  formatHist(histo)
  print 'number of counts in summed histogram: ' + str(histo.Integral())
  return histo


def createMCAFile(setName, mcaDirectory):
  filesToProcess = []
  for root, dir, files in os.walk(mcaDirectory):
    for file in files:
      filesToProcess.append(mcaDirectory+file)
  tehFiles = ' '
  print 'Found '+str(len(filesToProcess))+' files to process'
  for file in filesToProcess:
    tehFiles = tehFiles + ' '+file
  filename = setName+'MCA.root'
  cmd = 'majigorrootmca '
  os.system(cmd+tehFiles)
  os.system('mv TestMCAFile.root '+setName+'MCA.root')
  return filename


def formatHist(histo):
  histo.GetXaxis().SetTitle("Energy [keV]")
  histo.GetXaxis().CenterTitle(1)
  histo.GetYaxis().SetTitle("Counts")
  histo.GetYaxis().CenterTitle(1)
  histo.Sumw2()

def formatGraph(graph):
  formatHist(graph.GetHistogram())

def formatCalibGraph(graph):
  formatHist(graph.GetHistogram())
  graph.GetHistogram().GetYaxis().SetTitle("MCA")

def getFitFcn():
  fPeak = ROOT.TF1("fPeak", "[0]*(1/(2*[4]))*exp((pow([2],2)/(2*pow([4],2)))+(x-[1])/[4])*TMath::Erfc((x-[1])/(sqrt(2)*[2])  + [2]/(sqrt(2)*[4])) + pol2(5) + [3]/(1+exp((x-[1])*10))")
  fPeak.SetParName(0, "Peak Height")
  fPeak.SetParName(1, "Centroid")
  fPeak.SetParName(2, "Sigma")
  fPeak.SetParName(3, "Step Size")
  fPeak.SetParName(4, "Skew")
  fPeak.SetParName(5, "Const")
  fPeak.SetParName(6, "Linear")
  fPeak.SetParName(7, "Quadratic")
  fPeak.SetParameter(0, 1)
  fPeak.SetParameter(1, 1)
  fPeak.SetParameter(2, 3)
  fPeak.FixParameter(3, 0)
  fPeak.SetParameter(4, 2)
  fPeak.SetParLimits(4, 0, 20)
  return fPeak


def fitPeak(histo, fPeak,gammaline, ratio):
  fName = 'fPeak'
  mcaline = ratio*gammaline
  fG2 = ROOT.TF1("fG2", '([0]/(sqrt(2*pi)*[2]))*exp(-0.5*pow(x-[1],2)/pow([2],2)) + pol2(3)')
  histo.GetXaxis().SetRangeUser(mcaline-15, mcaline+15)
  c1 = ROOT.TCanvas("c1", "",600,400)
  histo.Fit('gaus', 'L')
  c1.Update()
  passFcnPars(fPeak)
  histo.GetXaxis().SetRangeUser(mcaline-45, mcaline+45)
  histo.Fit(fName)
  c1.Update()
  boo = 1
  peakFitValues = []
  while boo > 0:
    value = raw_input('q(uit), p(rint), r(efit), l(og-l refit), g(aus fit), c(hi^2 and prob), m(ore)')
    if value == 'm':
      print 'q(uit), p(rint), r(efit skew), l(og-l refit), g(aus + pol fit), c(hi^2 and prob of current fit),  w(rite), f(ix), u(nfix)'
    if value == 'q':
      boo = 0
    if value == 'c':
      print getChiSquareAndProb(histo,ROOT.gROOT.GetFunction(fName))
    if value == 'p':
      c1.Update()
      c1.Print('~/Desktop/zomg.pdf')
    if value == 'r':
      fName = 'fPeak'
      histo.Fit(fName)
      c1.Update()
    if value == 'l':
      histo.Fit(fName,'L')
      c1.Update()
    if value == 'g':
      fName = 'fG2'
      histo.Fit('gaus')
      fG2.SetParameters(ROOT.gROOT.GetFunction('gaus').GetParameters())
      histo.Fit('gaus')
      histo.Fit(fName)
      c1.Update()
      passFcnPars(fPeak)
    if value == 'f':
      parK = raw_input('fix which parameter(1-8)? ')
      parV = raw_input('fix it to what? ')
      fPeak.FixParameter(int(parK)-1, float(parV))
    if value == 'u':
      parK = raw_input('unfix which parameter(1-8)? ')
      fPeak.SetParLimits(int(parK)-1, 1,0)
    if value == 'w':
      getFitValues(histo, ROOT.gROOT.GetFunction(fName), peakFitValues)
      boo = 0
  return peakFitValues

def passFcnPars(f1):
  f1.SetParameters(ROOT.gROOT.GetFunction('gaus').GetParameters())
  f1.FixParameter(3,0)
  f1.SetParameter(4, 0.6)
  f1.SetParameter(5, ROOT.gROOT.GetFunction('pol0').GetParameter(0))

def getChiSquareAndProb(histo, f1):
  binA = histo.GetXaxis().GetFirst()
  binB = histo.GetXaxis().GetLast()
  ndf = 0
  sum = 0
  obs = 0
  expect = 0
  for k in range(binA, binB+1):
    expect = f1.Integral(histo.GetBinLowEdge(k), histo.GetBinLowEdge(k+1))
    obs = histo.GetBinContent(k)
    if(obs>0):
      ndf = ndf+1
      sum += 2*(expect-obs + obs*math.log(obs/expect))
  return ROOT.TMath.Prob(sum, ndf-9)



def calibratePoints(peakInfo, fName):
  # peak info is a list of lists(array)
  f1 = ROOT.gROOT.GetFunction(fName)
  print 'Calibrating: '+str(len(peakInfo)) + ' points found.'
  graph = ROOT.TGraphErrors()
  graphres = ROOT.TGraphErrors()
  graphAlt = ROOT.TGraphErrors()
  graphresAlt = ROOT.TGraphErrors()
  graph.Fit('pol1')
  c1 = ROOT.TCanvas("c1", "c1",404,756)
  c1.Divide(1,2)
  c1.cd(1)
  populateCalibGraph(graph, peakInfo)
  graph.Draw("AP")
  graph.Fit(f1, 'b')
  graph.Fit(f1, 'b')
  populateResidGraph(graphres, peakInfo, f1)
  c1.cd(2)
  c1.cd(2).SetGridy(1)
  graphres.Draw("AP")
  c1.Update()
  
  print 'P-value: ' + str(f1.GetProb())
  print 'Chi^2 / NDF: ' + str(f1.GetChisquare()) + '/' + str(f1.GetNDF())
  d = raw_input(' oh hai')
  c1.Print('~/Desktop/CalibrationGraphsI.pdf')

def populateCalibGraph(graph, peakInfo):
  for index, line in enumerate(peakInfo):
    if line[-2] > 0.05:

      graph.SetPoint(index, line[-1], line[2])
      graph.SetPointError(index, getGammaError(line[-1]), line[3])
  formatCalibGraph(graph)


def populateResidGraph(graphres, peakInfo, f1):
  for index, line in enumerate(peakInfo):
    graphres.SetTitle("#pi")
    graphres.SetPoint(index, line[-1], line[2]-f1.Eval(line[-1]))
    graphres.SetPointError(index, getGammaError(line[-1]), line[3])
    formatCalibGraph(graphres)
    graphres.GetYaxis().SetTitle('#Delta MCA')


def getFitValues(h1, f1, fitvals):
  del fitvals[:]
  print 'Writing fit values for ' + str(f1.GetName())
  for k in range(0,f1.GetNpar()):
    fitvals.append(f1.GetParameter(k))
    fitvals.append(f1.GetParError(k))
  fitvals.append(getChiSquareAndProb(h1,f1))


def getGammaError(gammaline):
  print 'getting error for gamma line of ' +str(gammaline)
  return getGammaDict()[gammaline]
  #return gammaDict[gammaline]


def getGammaDict():
  gammaDict = {}
  gammaDict[338.320] = 0.006
  gammaDict[583.187] = 0.002
  gammaDict[609.32] = 0.005
  gammaDict[661.657] = 0.003
  gammaDict[911.204] = 0.004
  gammaDict[968.971] = 0.017
  gammaDict[1173.226] = 0.003
  gammaDict[1332.492] = 0.004
  gammaDict[1460.822] = 0.01 
  gammaDict[1764.491] = 0.01 
  gammaDict[2614.511] = 0.01
  return gammaDict

