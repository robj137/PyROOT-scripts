#!/usr/bin/python

import ROOT
import CalibrateMods
import sys
import os
import pickle

usage = 'Usage: ./findPeaks DataSetName \n'

if len(sys.argv) < 2:
  print usage
  sys.exit()


#ROOT.TROOT.gApplication.ExecuteFile("~/rootlogon.C")

setName=sys.argv[1]
parentDirectory = '/Users/rob/Development/AnalysisToolkit/WIPPnRuns/CuShield/'

file = ROOT.TFile(setName+'Calibrated.root')
tree = file.Get('T')
tree.Draw('fEnergyCal>>h1(5000,0,5000)')
h1 = ROOT.gDirectory.Get('h1')
#h1.Sumw2()
h1.Draw("hist")

peakInfo = []

peakInfo = CalibrateMods.fitPeaks(h1)

output = open('Pickled'+setName+'Peaks.txt','w')
pickle.dump(peakInfo, output)
output.close()


