#!/usr/bin/python

import ROOT
import CalibrateMods
import sys
import os
import pickle

usage = 'Usage: '+str(sys.argv[0])+' DataSetName \n'

if len(sys.argv)<2:
  print usage
  sys.exit()


#ROOT.TROOT.gApplication.ExecuteFile("~/rootlogon.C")

f = open(sys.argv[1])
peakInfo = pickle.load(f)
livetime = 1
if sys.argv[1].find('Initial') > 0:
  livetime = 73.0
if sys.argv[1].find('NewCryostat') > 0:
  livetime = 62.55
if sys.argv[1].find('PbSheet') > 0:
  livetime = 11.90

for peak in peakInfo:
  if len(peak) == 17:
    print '& & ',
    print '{0:.2f}'.format(peak[-3]), '&', '{0:.2f}'.format(peak[-2]), '&',
    print '{0:.2f}'.format(peak[-5]/livetime), '&', '{0:.2f}'.format(peak[-5]/livetime), 
    print '& &', '%02d'%round(100*peak[-1]),
    print ' \\\\'
  print '& & ',
  print '{0:.2f}'.format(peak[2]), '&', '{0:.2f}'.format(peak[3]), '&',
  print '{0:.2f}'.format(peak[0]/livetime), '&', '{0:.2f}'.format(peak[1]/livetime), 
  print '& &', '%02d'%round(100*peak[-1]),
  print '{0:.1f}'.format(peak[-2]),
  print ' \\\\'

