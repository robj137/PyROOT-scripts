#!/usr/bin/python

import ROOT
import sys


ROOT.gROOT.ProcessLine(".X $MGDODIR/Igor/LoadMGDOIgorXIAClasses.C")
ROOT.gROOT.ProcessLine(".L $MGDODIR/lib/libMGDORoot.so")
ROOT.gROOT.ProcessLine(".L $ORDIR/lib/libORDataObjects.so")


myChain = ROOT.TChain("DGF")

filelist = sys.argv[:]
del filelist[0]

for file in filelist:
  if file.find('root'):
    myChain.AddFile(file)

nEntries = myChain.GetEntries()

print 'Found', nEntries, ' entries in chain'

myEvent = ROOT.ORDGFEvent()
myChain.SetBranchAddress('fDGFEvent', ROOT.AddressOf(myEvent))

myChain.GetEntry(0)

eventTimeOld = myEvent.GetEventTime()
bufferStart = myEvent.GetBufferTime();
runStart = bufferStart;
myChain.GetEntry(1);
eventTimeNew=myEvent.GetEventTime();
  
runTime = 0
liveTime = 0
triggerDeadTime = 0
nBuffers = 0
nEvents = 0
frac = 0.01
deficit = 0
nEvents = nEvents + 1
prevEnergy = myEvent.GetEnergy()

for i in range(1, nEntries):
  prevEnergy = myEvent.GetEnergy()
  myChain.GetEntry(i)
  if myEvent.GetBufferEventNumber() == 0 :
    runTime = runTime + eventTimeNew - bufferStart
    eventTimeOld = myEvent.GetBufferTime()
    bufferStart = myEvent.GetBufferTime()
    if prevEnergy > 0:
      deficit = deficit + bufferStart - eventTimeNew
    nBuffers = nBuffers + 1
  eventTimeNew = myEvent.GetEventTime()
  liveTime = liveTime + eventTimeNew - eventTimeOld
  if myEvent.GetEnergy() > 0:
    nEvents = nEvents + 1
  eventTimeOld = eventTimeNew

runEnd = eventTimeNew
print 'The total clock time is', str(float(runEnd)-float(runStart))
print 'The total deficit time is', str(deficit)
runTime = runTime + eventTimeNew - bufferStart
triggerDeadTime = (nEvents - nBuffers - 1)*23e-6
print 'The Pre-livetime is ', liveTime
print 'The trigger dead time is', triggerDeadTime
liveTime = liveTime - triggerDeadTime
print 'Found', nEvents, ' full events in ', str(nBuffers+1), 'buffers'
print 'RunTime: ', runTime
print 'LiveTime: ', liveTime
print '\% Live: ', str((liveTime/runTime)*100)
