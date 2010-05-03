#!/usr/bin/python

import ROOT
import CalibrateMods
import sys
import os
import pickle


usage = 'Usage: ./calibrate DataSetName arg\n e.g. DataSetName = NewCryostat\n'
usage += '  arg = find or fitlines or friendTree\n'

if len(sys.argv) < 2:
  print usage
  sys.exit()

  ratio = 1.0
if len(sys.argv) >3:
  ratio = float(sys.argv[3])

#ROOT.TROOT.gApplication.ExecuteFile("~/rootlogon.C")

setName=sys.argv[1]
parentDirectory = '/Users/rob/Development/AnalysisToolkit/WIPPnRuns/CuShield/'+setName+'/'
mcaDirectory = parentDirectory+'MCA/'
print mcaDirectory
if(sys.argv[2] == 'find'):
  filename = CalibrateMods.createMCAFile(setName,mcaDirectory)

  histo = CalibrateMods.getMCASumHist(filename, setName)
  peaks = [ 129.065, 209.253, 238.632, 270.245, 277.371, 300.087, 328.000, 
            338.320, 463.004, 583.187, 609.32, 661.657, 727.330, 
            794.947, 860.557, 911.204, 1173.226, 1332.492, 1460.822, 
            1588.20, 1592.511, 1764.491, 2103.511, 2614.511]
  peakInfo = []
  for peak in peaks:
    peakFit = CalibrateMods.fitPeak(histo, peak, ratio)
    if len(peakFit) > 0:
      peakFit.append(peak)
      peakInfo.append(peakFit)

  output = open('PickledCalibration'+setName+'.txt','w')
  pickle.dump(peakInfo, output)
  output.close()

if(sys.argv[2] == 'fitlines'):
  f = open('PickledCalibration'+setName+'.txt')
  peakInfo = pickle.load(f)
  val = raw_input(' What order polynomial?: ')
  if int(val) < 6:
    CalibrateMods.calibratePoints(peakInfo,val, setName)

if(sys.argv[2] == 'friendTree'):
  ftree =  CalibrateMods.createCalibratedFriend(setName, parentDirectory)
