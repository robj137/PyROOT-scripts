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


def formatGraph(graph):
  formatHist(graph.GetHistogram())


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
  mcaline = ratio*gammaline
  histo.GetXaxis().SetRangeUser(mcaline-15, mcaline+15)
  c1 = ROOT.TCanvas("c1", "")
  histo.Fit('gaus', 'L')
  c1.Update()
  passFcnPars(fPeak)
  histo.GetXaxis().SetRangeUser(mcaline-45, mcaline+45)
  histo.Fit('fPeak')
  c1.Update()
  boo = 1
  peakFitValues = []
  while boo > 0:
    value = raw_input('  q(uit), p(rint), r(efit), l(og-l refit), c(hi^2 and prob), w(rite)')
    if value == 'q':
      boo = 0
    if value == 'c':
      print getChiSquareAndProb(histo,fPeak)
    if value == 'p':
      c1.Update()
      c1.Print('~/Desktop/zomg.pdf')
    if value == 'r':
      histo.Fit('fPeak')
      c1.Update()
    if value == 'l':
      histo.Fit('fPeak','L')
      c1.Update()
    if value == 'g':
      histo.Fit('gaus')
      c1.Update()
      passFcnPars(fPeak)
    if value == 'w':
      getFitValues(histo, fPeak, peakFitValues)
      print 'number of entries in fitval: '+ str(len(peakFitValues))
  return peakFitValues

def passFcnPars(f1):
  f1.SetParameters(ROOT.gROOT.GetFunction('gaus').GetParameters())
  f1.FixParameter(3,0)
  f1.SetParameter(4, 0.6)


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



def calibratePoints(peakInfo):




def getFitValues(h1, f1, fitvals):
  del fitvals[:]
  for k in range(0,f1.GetNpar()):
    fitvals.append(f1.GetParameter(k))
    fitvals.append(f1.GetParError(k))
  fitvals.append(getChiSquareAndProb(h1,f1))
