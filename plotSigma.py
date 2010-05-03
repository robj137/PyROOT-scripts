#!/usr/bin/python

import ROOT
import CalibrateMods
import sys
import os
import pickle

usage = 'Usage: '+str(sys.argv[0])+ 'DataSetName \n'

if len(sys.argv) < 2:
  print usage
  sys.exit()


#ROOT.TROOT.gApplication.ExecuteFile("~/rootlogon.C")

setName=sys.argv[1]
parentDirectory = '/Users/rob/Development/AnalysisToolkit/WIPPnRuns/CuShield/'

f = open('PickledCalibration'+setName+'.txt')
peakInfo = pickle.load(f)
CalibrateMods.resolvePoints(peakInfo, setName)


