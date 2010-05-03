#!/usr/bin/python

import ROOT
import sys
import MyPyRoot

ROOT.gROOT.ProcessLine(".X $MGDODIR/Igor/LoadMGDOIgorXIAClasses.C")
ROOT.gROOT.ProcessLine(".L $MGDODIR/lib/libMGDORoot.so")
ROOT.gROOT.ProcessLine(".L $ORDIR/lib/libORDataObjects.so")
  
#ROOT.gROOT.ProcessLine( "struct MyStruct {\
#  TDatime fDatime; \
#};" )

#mystruct = ROOT.MyStruct()
filelist = sys.argv[:]

del filelist[0]

fSave = ROOT.TFile.Open('DateFriendTree.root', 'RECREATE')
myChain = MyPyRoot.getChainFromList(filelist, 'DGF')

nEntries = myChain.GetEntries()

fDatime = ROOT.TDatime()

myEvent = ROOT.ORDGFEvent()
myHeader = ROOT.ORDGFHeader()
myChain.SetBranchAddress('fDGFHeader', ROOT.AddressOf(myHeader))

dateTree = ROOT.TTree('dateTree','')
dateTree.Branch('fDatime', fDatime)

for i in range(0, nEntries):
  myChain.GetEntry(i)
  theFileName = myHeader.GetFileName()
  year, month, day = MyPyRoot.getDateFromString(theFileName)
  fDatime.Set(int(year), int(month), int(day), 0, 0, 0)
  dateTree.Fill()  
  

dateTree.Write()
fSave.Close()
