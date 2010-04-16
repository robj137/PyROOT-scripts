#!/usr/bin/python

import ROOT
import CalibrateMods
import sys
import os
import pickle

usage = 'Usage: ./calibrate DataSetName arg\n e.g. DataSetName = NewCryostat\n'
usage += '  arg = find or fitlines\n'

if len(sys.argv) < 2:
  print usage
  sys.exit()

ratio = 4.83

#ROOT.TROOT.gApplication.ExecuteFile("~/rootlogon.C")

setName=sys.argv[1]
parentDirectory = '/Users/rob/Development/AnalysisToolkit/WIPPnRuns/CuShield/'+setName+'/'
mcaDirectory = parentDirectory+'MCA/'
print mcaDirectory
if(sys.argv[2] == 'find'):
  filename = CalibrateMods.createMCAFile(setName,mcaDirectory)


  histo = CalibrateMods.getMCASumHist(filename, setName)
  fPeak = CalibrateMods.getFitFcn()
  peaks = [609.32, 661.66, 1173.28, 1332.49, 1460.82, 1764.49, 2614.51]
  peakInfo = []
  for peak in peaks:
    peakFit = CalibrateMods.fitPeak(histo, fPeak,peak, ratio)
    peakFit.append(peak)
    peakInfo.append(peakFit)

  output = open('PickledCalibPoints.txt','w')
  pickle.dump(peakInfo, output)
  output.close()

if(sys.argv[2] == 'fitlines'):
  CalibrateMods.calibratePoints(parentDirectory+'CalibrationResults.txt')





