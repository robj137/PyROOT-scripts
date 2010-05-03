#!/usr/bin/python

import DGFSet
import os
import sys

getRunTime = DGFSet.getRunTime
usage = 'USAGE: '+sys.argv[0] + ' FILE.set'

if len(sys.argv)<2 :
  print usage
else:
  filename = sys.argv[1]
  setvals = DGFSet.getSetFileValues(filename)
  
  slowlen = DGFSet.get(setvals, 'SLOWLENGTH0')
  fastlen = DGFSet.get(setvals, 'FASTLENGTH0')
  slowgap = DGFSet.get(setvals, 'SLOWGAP0')
  fastgap = DGFSet.get(setvals, 'FASTGAP0')
  peaksep = DGFSet.getPeakSep(setvals)
  runtime = getRunTime(setvals)
  deadtime = DGFSet.getDeadTime(setvals)
  livetime = DGFSet.getLiveTime(setvals)
  numevents = DGFSet.getNumberEvents(setvals)
  fastpeaks = DGFSet.getFastPeaks(setvals)
  ocr = DGFSet.getNumberEvents(setvals)/getRunTime(setvals)
  icr = runtime*ocr/livetime
  ftdt = runtime - fastpeaks/icr
  decimation = DGFSet.get(setvals, 'DECIMATION')

  print '	DECIMATION:		'+str(decimation)
  print '	SLOWLENGTH:		'+str(slowlen)
  print '	FASTLENGTH:		'+str(fastlen)
  print '	SLOWGAP:		'+str(slowgap)
  print '	FASTGAP:		'+str(fastgap)
  print '	PEAKSEP:		'+str(peaksep)
  print '	ICR:			'+str(icr)
  print '	OCR:			'+str(ocr)
  print '	FTDT:			'+str(ftdt)
  print '	LIVETIME:		'+str(livetime)
  print '	DEADTIME:		'+str(deadtime)
  print '	RUNTIME:		'+str(runtime)
  print '	fastpeaks		'+str(fastpeaks)
  print '	NUMEVENTS:		'+str(numevents)
  print '	Diff run-ftdt-lt-dt:	'+str(runtime-ftdt - livetime-deadtime)

  #print DGFSet.getAllPairs(setvals)
