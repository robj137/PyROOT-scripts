#!/usr/bin/python

import ROOT
ROOT.gApplication.ExecuteFile("~/rootlogon.C")
import math
import sys
import os

def accessCommandLine(): # for use in scripts
  input = raw_input('ROOT: ')
  ROOT.gROOT.ProcessLine(input)


def typicalInput():
  input = raw_input('a(ccess root), q(uit), w(rite), p(rint), m(ore)')
  if input == 'q':
    return 0
  if input == 'a':
    accessCommandLine()
  if input == 'p':
    input2 = raw_input('~/Desktop/InvaderZim.pdf or pick ur own: ')
    if len(input2) > 0:
      filename = input2
    else:
      filename = '~/Desktop/InvaderZim.pdf'
    aCanvas = ROOT.gROOT.FindObject('c1')
    if(aCanvas):
      if(aCanvas.InheritsFrom("c1")):
        aCanvas.Print(filename)
        return 1
    return -1 # fail!


def makeMCAHistFromChain(aChain):
  #assumes that energy is fEnergy
  aChain.Draw('fEnergy>>h1(65536,0,65536)')
  h1 = ROOT.gROOT.Get('h1')
  return h1

def getChainFromList(aFilelist, chainName):
  aChain = ROOT.TChain(chainName)
  for entry in aFilelist:
    aChain.AddFile(entry)
  return aChain

def getDateFromString(aString):
  #first 4 digits are year
  year = aString[0:4]
  if aString.find('-') >-1:
    month = aString[5:7]
    day = aString[8:10]
  else:
    month = aString[4:6]
    day = aString[6:8]
  return year, month, day

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

def getMCAFileName(setName):
  filename = setName+'MCA.root'
  return filename

def formatHist(histo):
  histo.GetXaxis().SetTitle("MCA")
  #histo.GetXaxis().SetTitle("Energy [keV]")
  histo.GetXaxis().CenterTitle(1)
  histo.GetYaxis().SetTitle("Counts")
  histo.GetYaxis().CenterTitle(1)
  histo.Sumw2()

def formatGraph(graph):
  formatHist(graph.GetHistogram())

def formatCalibGraph(graph):
  formatHist(graph.GetHistogram())
  graph.GetHistogram().GetYaxis().SetTitle("MCA")
  graph.GetHistogram().GetXaxis().SetTitle("Energy")

def formatResolutionGraph(graph):
  formatHist(graph.GetHistogram())
  graph.GetHistogram().SetMinimum(0)
  graph.GetHistogram().GetYaxis().SetTitle("#sigma [keV]")
  graph.GetHistogram().GetXaxis().SetTitle("Energy")
  graph.GetHistogram().SetBins(100, 0, 3000)

def getFitFcn():
  fPeak = ROOT.TF1("fPeak", "[0]*(1/(2*[3]))*exp((pow([2],2)/(2*pow([3],2)))+(x-[1])/[3])*TMath::Erfc((x-[1])/(sqrt(2)*[2])  + [2]/(sqrt(2)*[3])) + pol2(4)")
  fPeak.SetParName(0, "Area")
  fPeak.SetParName(1, "Centroid")
  fPeak.SetParName(2, "Sigma")
  fPeak.SetParName(3, "Skew")
  fPeak.SetParName(4, "Const")
  fPeak.SetParName(5, "Linear")
  fPeak.SetParName(6, "Quadratic")
  fPeak.SetParLimits(0, 0, 1e10)
  fPeak.SetParLimits(2, 0.1, 1e10)
  fPeak.SetParameter(0, 1)
  fPeak.SetParameter(1, 1)
  fPeak.SetParameter(2, 3)
  fPeak.SetParameter(3, 2)
  fPeak.SetParLimits(3, 0, 20)
  return fPeak

def getDoubleGausFitFcn():
  f2G2 = ROOT.TF1("f2G2", '([0]/(sqrt(2*pi)*[2]))*exp(-0.5*pow(x-[1],2)/pow([2],2)) + pol2(3) + ([6]/(sqrt(2*pi)*[2]))*exp(-0.5*pow(x-[7],2)/pow([2],2))')
  f2G2.SetParName(0, "Area 1")
  f2G2.SetParName(1, "Centroid 1")
  f2G2.SetParName(2, "Sigma")
  f2G2.SetParName(3, "Const")
  f2G2.SetParName(4, "Linear")
  f2G2.SetParName(5, "Quadratic")
  f2G2.SetParName(6, "Area 2")
  f2G2.SetParName(7, "Centroid 2")
  f2G2.SetParLimits(0, 0, 1e10)
  f2G2.SetParLimits(6, 0, 1e10)
  return f2G2

def fromFunk2Funk(f1, f2):
  f2.SetParameters(f1.GetParameters())

def getGausFitFcn():
  fG2 = ROOT.TF1("fG2", '([0]/(sqrt(2*pi)*[2]))*exp(-0.5*pow(x-[1],2)/pow([2],2)) + pol2(3)')
  fG2.SetParName(0, "Area")
  fG2.SetParName(1, "Centroid")
  fG2.SetParName(2, "Sigma")
  fG2.SetParName(3, "Const")
  fG2.SetParName(4, "Linear")
  fG2.SetParName(5, "Quadratic")
  return fG2

def fitPeaks(histo):
  fG2 = getGausFitFcn()
  f2G2 = getDoubleGausFitFcn()
  c1 = ROOT.TCanvas("c1", "",600,400)
  pt = ROOT.TPaveText()
  pt.SetX1NDC(0.22)
  pt.SetX2NDC(0.32)
  pt.SetY1NDC(0.6)
  pt.SetY2NDC(0.8)
  pt.AddText('P-value:')
  pt.AddText('Significance:')
  pt.SetBorderSize(0)
  tPVal = pt.GetLineWith('P-value:')
  tSigVal = pt.GetLineWith('Significance:')
  boo = 1
  peakFitValues = []
  histo.Draw("ehist")
  while boo > 0:
    value = raw_input('a(ccess root), q(uit), d(ouble down!), w(rite), p(rint), r(efit), l(og-l refit), g(aus fit), c(hi^2 and prob), m(ore)')
    print 'q(uit), p(rint), r(efit skew), l(og-l refit), g(aus + pol fit), c(hi^2 and prob of current fit),  w(rite), f(ix), u(nfix)'
    if value == 'q':
      boo = 0
    if value == 'a':
      accessCommandLine()
    if value == 'd':
      fromFunk2Funk(fG2,f2G2)
      offset = raw_input("What's the offset of the 2nd peak? ")
      frac = raw_input("And what's the approx. ratio of the areas (2nd/1st)? ")
      f2G2.SetParameter(6, float(frac)*fG2.GetParameter(0))
      f2G2.SetParameter(7, float(offset)+fG2.GetParameter(1))
      histo.Fit(f2G2)
      c1.Update()
    if value == 'c':
      pval = getChiSquareAndProb(histo,fG2)
      signif = getPeakSignificance(fG2)
      pvalT = '%.3f'%float(pval)
      sigT = '%.1f'%float(signif)
      tPVal.SetText(0,0,'P-Value: '+pvalT)
      tSigVal.SetText(0,0,'Significance: '+sigT)
      pt.Draw()
      c1.Update()
    if value == 'cd':
      pval = getChiSquareAndProb(histo,f2G2)
      pvalT = '%.3f'%float(pval)
      tPVal.SetText(0,0,'P-Value: '+pvalT)
      pt.Draw()
      c1.Update()
    if value == 'p':
      c1.Update()
      c1.Print('~/Desktop/zomg.pdf')
    if value == 'r':
      histo.Fit(fG2)
      c1.Update()
    if value == 'l':
      histo.Fit(fG2,'LI')
      c1.Update()
    if value == 'li':
      histo.Fit(fG2,'L')
      c1.Update()
    if value == 'dl':
      histo.Fit(f2G2,'LI')
      c1.Update()
    if value == 'g':
      histo.Fit('gaus')
      fG2.SetParameters(ROOT.gROOT.GetFunction('gaus').GetParameters())
      histo.Fit(fG2)
      c1.Update()
    if value == 'f':
      fG2.Print()
      parK = raw_input('fix which parameter(1-6)? ')
      parV = raw_input('fix it to what? ')
      fG2.FixParameter(int(parK)-1, float(parV))
    if value == 'df':
      f2G2.Print()
      parK = raw_input('fix which parameter(1-8)? ')
      parV = raw_input('fix it to what? ')
      f2G2.FixParameter(int(parK)-1, float(parV))
    if value == 'u':
      fG2.Print()
      parK = raw_input('unfix which parameter(1-8)? ')
      fG2.SetParLimits(int(parK)-1, 1,0)
    if value == 'du':
      f2G2.Print()
      parK = raw_input('unfix which parameter(1-8)? ')
      f2G2.SetParLimits(int(parK)-1, 1,0)
    if value == 'w':
      fitvalue = getFitValue(histo, fG2)
      fitvalue.append(getPeakSignificance(fG2))
      fitvalue.append(getChiSquareAndProb(histo, fG2))
      peakFitValues.append(fitvalue)
    if value == 'wd':
      fitvalue = getFitValue(histo, f2G2)
      fitvalue.append(getChiSquareAndProb(histo, f2G2))
      peakFitValues.append(fitvalue)
  return peakFitValues


def fitPeak(histo,gammaline, ratio):
  fName = 'fPeak'
  fPeak = getFitFcn()
  fG2 = getGausFitFcn()
  f2G2 = getDoubleGausFitFcn()
  mcaline = ratio*gammaline
  histo.GetXaxis().SetRangeUser(mcaline-15, mcaline+15)
  c1 = ROOT.TCanvas("c1", "",600,400)
  pt = ROOT.TPaveText()
  pt.SetX1NDC(0.22)
  pt.SetX2NDC(0.32)
  pt.SetY1NDC(0.6)
  pt.SetY2NDC(0.8)
  pt2 = pt.Clone('pt')
  pt2.SetX1NDC(0.6)
  pt2.SetX2NDC(0.75)
  pt2.SetY1NDC(0.2)
  pt2.SetY2NDC(0.3)
  pt2.AddText(str(gammaline))
  pt.AddText('P-value:')
  pt.SetBorderSize(0)
  tPVal = pt.GetLineWith('P-value:')
  histo.Fit('gaus', 'L')
  c1.Update()
  passFcnPars(fPeak)
  passFcnPars(fG2)
  histo.GetXaxis().SetRangeUser(mcaline-45, mcaline+45)
  histo.Fit(fName)
  pt2.Draw()
  c1.Update()
  boo = 1
  peakFitValues = []
  while boo > 0:
    pt2.Draw()
    c1.Update()
    value = raw_input('q(uit), p(rint), d(ouble), r(efit), l(og-l refit), g(aus fit), c(hi^2 and prob), m(ore)')
    if value == 'a':
      accessCommandLine()
    if value == 'm':
      print 'q(uit), p(rint), r(efit skew), l(og-l refit), g(aus + pol fit), c(hi^2 and prob of current fit),  w(rite), f(ix), u(nfix)'
    if value == 'q':
      boo = 0
    if value == 'c':
      pval = getChiSquareAndProb(histo,ROOT.gROOT.GetFunction(fName))
      pvalT = '%.3f'%float(pval)
      tPVal.SetText(0,0,'P-Value: '+pvalT)
      pt.Draw()
      c1.Update()
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
    if value == 'd':
      fName = 'f2G2'
      fromFunk2Funk(fG2,f2G2)
      offset = raw_input("What's the offset of the 2nd peak? ")
      frac = raw_input("And what's the approx. ratio of the areas (2nd/1st)? ")
      f2G2.SetParameter(6, float(frac)*float(fG2.GetParameter(0)))
      f2G2.SetParameter(7, float(offset)+fG2.GetParameter(1))
      histo.Fit(f2G2)
      c1.Update()
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
    if value == 's':
      getFitValues(histo, ROOT.gROOT.GetFunction(fName), peakFitValues)
      boo = 0
  return peakFitValues

def gausGives(f1):
  height = ROOT.gROOT.GetFunction('gaus').GetParameter(0)
  sigma = ROOT.gROOT.GetFunction('gaus').GetParameter(2)
  f1.SetParameters(ROOT.gROOT.GetFunction('gaus').GetParameters())
  f1.SetParameter(0, ROOT.TMath.Sqrt(2*3.14159)*height*sigma)
  f1.SetParameter(3, 0.6)
  f1.SetParameter(4, ROOT.gROOT.GetFunction('pol0').GetParameter(0))


def passFcnPars(f1):
  height = ROOT.gROOT.GetFunction('gaus').GetParameter(0)
  sigma = ROOT.gROOT.GetFunction('gaus').GetParameter(2)
  f1.SetParameters(ROOT.gROOT.GetFunction('gaus').GetParameters())
  f1.SetParameter(0, ROOT.TMath.Sqrt(2*3.14159)*height*sigma)
  f1.SetParameter(3, 0.6)
  f1.SetParameter(4, ROOT.gROOT.GetFunction('pol0').GetParameter(0))

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
    if obs > 0 and expect > 0:
      expect = expect / histo.GetBinWidth(k)
      ndf = ndf+1
      sum += 2*(expect-obs + obs*math.log(obs/expect))
  print sum, ndf-6
  return ROOT.TMath.Prob(sum, ndf-8)

def getResolutionFcn():
  fRes = ROOT.TF1('fRes', 'sqrt([0]+[1]*x+[2]*x*x)')
  fRes.SetParLimits(0, 0, 10)
  fRes.SetParLimits(1, 0, 1e4)
  fRes.SetParLimits(2, 0, 1e4)
  fRes.SetParameter(0,1)
  fRes.SetParameter(1,1)
  fRes.FixParameter(2,0)
  return fRes

def resolvePoints(peakInfo, setName):
  graph = ROOT.TGraphErrors()
  graph.SetName('graph')
  populateResolutionGraph(graph, peakInfo)
  c1 = ROOT.TCanvas("c1", "c1",644,728)
  graph.Draw('ap')
  fRes = getResolutionFcn()
  graph.Fit(fRes)
  c1.Update()
  boo = 1
  while(boo > 0):
    print ('whacha wanna do? a(ccess command line) r(efit) q(uit) p(rint)? ')
    val = raw_input('remo(v)e point  ')
    if(val == 'q'):
      boo = 0
    elif(val == 'r'):
      graph.Fit(fRes)
      c1.Update()
    elif(val == 'a'):
      accessCommandLine()
    elif(val == 'p'):
      c1.Print('~/Desktop/ResolutionPlot.pdf')
    elif(val == 'v'):
      graph.Print()
      input = raw_input('remove which point? ')
      graph.RemovePoint(int(input))

def calibratePoints(peakInfo, order,setName):
  fName = 'pol'+str(order)
  # peak info is a list of lists(array)
  c1 = ROOT.TCanvas("c1", "c1",644,728)
  c1.SetGridy(1)
  boo = 1
  pt = ROOT.TPaveText()
  pt.SetTextSize(0.05)
  pt.SetX1NDC(0.52)
  pt.SetX2NDC(0.92)
  pt.SetY1NDC(0.7)
  pt.SetY2NDC(0.9)
  pt.AddText(setName)
  pt.AddLine(0, 0.75, 1, 0.75)
  pt.AddText('Poly Order: ')
  pt.AddText('P-value: ' + str(order))
  pt.AddText('x-s')
  pt.SetBorderSize(2)
  tPVal = pt.GetLineWith('P-value:')
  tOrder = pt.GetLineWith('Poly Order:')
  tXs = pt.GetLineWith('x-s')
  fPol = getPolFcn(order)
  while boo > 0:
    f1 = ROOT.gROOT.GetFunction(fName)
    print 'Calibrating: '+str(len(peakInfo)) + ' points found.'
    graph = ROOT.TGraphErrors()
    graphres = ROOT.TGraphErrors()
    graphres.SetMarkerSize(1.8)
    graphres.SetMarkerStyle(23)
    graphAlt = ROOT.TGraphErrors()
    graphresAlt = ROOT.TGraphErrors()
    populateCalibGraph(graph, peakInfo)
    populateAltCalibGraph(graphAlt, peakInfo)
    print 'graph has ' + str(graph.GetN()) + ' points'
    graph.Draw("AP")
    graph.Fit('pol2')
    for i in range(1, int(order)+1):
      graph.Fit('pol'+str(order),'B')
      ROOT.gROOT.GetFunction('pol'+str(i+1)).SetParameters(ROOT.gROOT.GetFunction('pol'+str(i)).GetParameters())
    fPol.SetParameters(ROOT.gROOT.GetFunction('pol'+str(order)).GetParameters())
    graph.Fit(fPol)
    graphAlt.Fit(fPol)
    graph.Fit(fPol)
    populateResidGraph(graphres, peakInfo, fPol)
    print 'graphres has ' + str(graphres.GetN()) + ' points'
    graphres.Draw("AP")
    prob = fPol.GetProb()
    chisndf = '#chi^{2}/ndf = '
    chisndf = chisndf + '{0:.3f} / {1:d})'.format(fPol.GetChisquare(),fPol.GetNDF())
    pvalT = '%.3f'%float(prob)
    tOrder.SetText(0,0,'Poly Order: '+str(order))
    tPVal.SetText(0,0,'P-Value: '+pvalT)
    tXs.SetText(0,0,chisndf)
    pt.Draw()
    c1.Update()
    print 'P-value: ' + str(prob)
    print 'Chi^2 / NDF: ' + str(fPol.GetChisquare()) + '/' + str(fPol.GetNDF())
    print 'mca value for 5300 keV: ', fPol.Eval(5300)
    print 'mca value for 8800 keV: ', fPol.Eval(8800)
    val = raw_input(' n(ew fit), q(uit), p(rint pdf), r(emove point), r(e)fit')
    if(val == 'a'):
      accessCommandLine()
    if(val == 'e'):
      graph.Fit('pol'+str(order))
      fPol.SetParameters(ROOT.gROOT.GetFunction('pol'+str(order)).GetParameters())
    if(val == 'n'):
      order = raw_input('Which order polynomial? ')
      fPol = getPolFcn(order)
      fName = 'pol'+order
    if(val == 'r'):
      print('Remove which point?')
      for index, line in enumerate(peakInfo):
        print index, line[-1], line[2]
      whichPoint = raw_input('Remove which point? ')
      peakInfo.pop(int(whichPoint))
    if(val == 'p'):
      name = raw_input('Base name of pdf? ')
      c1.Print('~/Desktop/'+name+fName+'.pdf')
    if(val == 'q'):
      boo = 0

def populateResolutionGraph(graph, peakInfo):
  for index, line in enumerate(peakInfo):
    if line[-2] > 0.01 and line[-3] > 1:
      ratio = line[-1]/line[2]
      graph.SetPoint(index, line[-1], line[4]*ratio)
      graph.SetPointError(index, getGammaError(line[-1]), line[5]*ratio)
      print 'significance:', line[-3],
      print 'p-value:', line[-2]
  formatResolutionGraph(graph)

def populateCalibGraph(graph, peakInfo):
  for index, line in enumerate(peakInfo):
    if line[-2] > 0.01:
      graph.SetPoint(index, line[-1], line[2])
      graph.SetPointError(index, getGammaError(line[-1]), line[3])
  formatCalibGraph(graph)

def populateAltCalibGraph(graph, peakInfo):
  for index, line in enumerate(peakInfo):
    if line[-2] > 0.01:
      graph.SetPoint(index, line[2], line[-1])
      graph.SetPointError(index, line[3],getGammaError(line[-1]))
  formatCalibGraph(graph)


def populateResidGraph(graphres, peakInfo, f1):
  for index, line in enumerate(peakInfo):
    if line[-2] > 0.01:
      graphres.SetTitle("")
      graphres.SetPoint(index, line[-1], line[2]-f1.Eval(line[-1]))
      graphres.SetPointError(index, getGammaError(line[-1]), line[3])
      formatCalibGraph(graphres)
      graphres.GetYaxis().SetTitle('#Delta MCA')
      graphres.GetXaxis().SetTitle('Energy [keV]')


def getFitValues(h1, f1, fitvals):
  del fitvals[:]
  print 'Writing fit values for ' + str(f1.GetName())
  for k in range(0,f1.GetNpar()):
    fitvals.append(f1.GetParameter(k))
    fitvals.append(f1.GetParError(k))
  fitvals.append(getPeakSignificance(f1))
  fitvals.append(getChiSquareAndProb(h1,f1))

def getFitValue(h1, f1):
  fitval = []
  for k in range(0, f1.GetNpar()):
    fitval.append(f1.GetParameter(k))
    fitval.append(f1.GetParError(k))
  return fitval

def getGammaError(gammaline):
  print 'getting error for gamma line of ' +str(gammaline)
  return getGammaDict()[gammaline]
  #return gammaDict[gammaline]


def getGammaDict():
  gammaDict = {}
  gammaDict[129.065] = 0.001
  gammaDict[209.253] = 0.006
  gammaDict[238.632] = 0.002
  gammaDict[240.986] = 0.006
  gammaDict[270.245] = 0.002
  gammaDict[277.371] = 0.005
  gammaDict[300.087] = 0.010
  gammaDict[328.000] = 0.006
  gammaDict[338.320] = 0.003
  gammaDict[463.004] = 0.006
  gammaDict[583.187] = 0.002
  gammaDict[609.32] = 0.005
  gammaDict[661.657] = 0.003
  gammaDict[727.330] = 0.009
  gammaDict[794.947] = 0.005
  gammaDict[860.557] = 0.004
  gammaDict[911.204] = 0.004
  gammaDict[964.766] = 0.010
  gammaDict[968.971] = 0.017
  gammaDict[1173.226] = 0.003
  gammaDict[1332.492] = 0.004
  gammaDict[1460.822] = 0.01 
  gammaDict[1588.200] = 0.03 
  gammaDict[1592.511] = 0.02 
  gammaDict[1764.491] = 0.01 
  gammaDict[2103.511] = 0.01
  gammaDict[2614.511] = 0.02
  return gammaDict

def getPolFcn(order):
  form = '[0]'
  for i in range(0, int(order)):
    form = form + '+['+str(i+1)+']*pow(x,'+str(i+1)+')'

  fPol = ROOT.TF1('fPol', form)
  return fPol


def createCalibratedFriend(setName, directory):
  filename = getMCAFileName(setName)
  hist = getMCASumHist(filename, setName)
  calibFile = open(directory+'calibrate.txt')
  calibCoeffs =  (calibFile.readline()).split()
  from ROOT import energyC
  energy = energyC()
  f = ROOT.TFile( setName+'Calibrated.root', 'RECREATE')
  tree = ROOT.TTree('T', '')
  tree.Branch( 'fEnergyCal', ROOT.AddressOf(energy, 'fEnergyCal' ), 'fEnergyCal/D')
  for i in range(50, 65536):
    if(i%1000 == 0): print i
    for entries in range(0, int(hist.GetBinContent(i))):
      energy.fEnergyCal = getCalibratedEnergy(i+ROOT.gRandom.Uniform(), calibCoeffs)
      tree.Fill()
  tree.Write()
  f.Close()

def getCalibratedEnergy(index, calibCoeffs):
  energy = 0.0
  for order, coeff in enumerate(calibCoeffs):
    energy = energy + ROOT.pow(index,order)*float(coeff)
  return energy


def writeCalibratedFile(setName, parentDirectory, ftree):
  filename = parentDirectory+setName+'.root'
  print filename
  f1 = ROOT.TFile.Open(filename, 'RECREATE')
  ftree.Write()
  f1.Close()

def getPeakSignificance(f1):
  sigma = f1.GetParameter(2)
  centroid = f1.GetParameter(1)
  bg = getBackgroundIntegral(f1, centroid-2.5*sigma, centroid+2.5*sigma)
  return f1.GetParameter(0)*0.998/ROOT.TMath.Sqrt(bg)

def getBackgroundIntegral(f1,a,b):
  #assumes f1 is some function with a 2-d polynomial, starting at index 3
  A = f1.GetParameter(3)
  B = f1.GetParameter(4)
  C = f1.GetParameter(5)
  return A*(b-a) + 0.5*B*(b*b-a*a) + (C/3)*(b*b*b-a*a*a)


