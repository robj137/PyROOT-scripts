#!/usr/bin/python
import struct


def getSetFileValues(filename):
  f = open(filename, 'rb')
  r = f.read()
  values = []
  for i in range(0,416):
    values.append(struct.unpack_from('H', r, 2*i)[0])

  return values

def getTripleTime(setfilevals,firstIndex):
  time = 25e-9*getTripleValue(setfilevals,firstIndex)
  return time

def getTripleValue(setfilevals,firstIndex):
  val = 2**32*setfilevals[firstIndex]
  val = val + 2**16*setfilevals[firstIndex+1]
  val = val + setfilevals[firstIndex+2]
  return val

def getNumberEvents(setfilevals):
  return getTripleValue(setfilevals,266)

def getFastPeaks(setfilevals):
  return getTripleValue(setfilevals,322)

def getRealTime(setfilevals):
  return getTripleTime(setfilevals,257)

def getRunTime(setfilevals):
  return getTripleTime(setfilevals,260)

def getLiveTime(setfilevals):
  return getTripleTime(setfilevals,319)

def getDeadTime(setfilevals):
  return getTripleTime(setfilevals,325)

def get(setfilevals, val):
  return setfilevals[getPolarisKeyNumber(val)]

def getRunTask(setfilevals):
  return setfilevals[getPolarisKeyNumber('RUNTASK')]

def getPeakSep(setfilevals):
  return setfilevals[getPolarisKeyNumber('PEAKSEP0')]

def getPolarisKeyNumber(par):
  pvd = getPolarisVarDict()
  return int(pvd[par])



def getAllPairs(setfilevals):
  dicto = getPolarisVarDict()
  for keys, vals in dicto.iteritems():
    print keys, setfilevals[int(vals)]

def getPolarisVarDict():
  d = {'MODNUM':'0', 'MODCSRA':'1', 'MODCSRB':'2', 'MODFORMAT':'3', 
       'SUMDAC':'4', 'RUNTASK':'5', 'CONTROLTASK':'6', 'MAXEVENTS':'7', 
       'COINCPATTERN':'8', 'COINCWAIT':'9', 'SYNCHWAIT':'10', 'INSYNCH':'11', 
       'REQTIMEA':'12', 'REQTIMEB':'13', 'REQTIMEC':'14', 'HOSTIO':'15', 
       'U00':'19', 'XDATLENGTH':'47', 'USERIN':'48', 'CHANCSRA0':'64', 
       'CHANCSRB0':'65', 'GAINDAC0':'66', 'TRACKDAC0':'67', 'SGA0':'68', 
       'UNUSEDA0':'69', 'ADJUSTOFFSETS0':'70', 'BASEPERRULE0':'71', 
       'SLOWLENGTH0':'72', 'SLOWGAP0':'73', 'FASTLENGTH0':'74', 'FASTGAP0':'75',
       'PEAKSAMPLE0':'76', 'PEAKSEP0':'77', 'FASTADCTHR0':'78', 
       'FASTTHRESH0':'79', 'MINWIDTH0':'80', 'MAXWIDTH0':'81', 
       'PAFLENGTH0':'82', 'TRIGGERDELAY0':'83', 'RESETDELAY0':'84', 
       'FTPWIDTH0':'85', 'TRACELENGTH0':'86', 'XWAIT0':'87', 'ENERGYLOW0':'88', 
       'LOG2EBIN0':'89', 'CFDTHR0':'90', 'PSAOFFSET0':'91', 'PSALENGTH0':'92', 
       'GAIN0':'93', 'BLCUT0':'94', 'U50':'95', 'TCOEFF0':'97', 
       'PREAMPGAINA0':'98', 'PREAMPGAINB0':'99', 'UNUSEDB0':'100', 
       'INTEGRATOR0':'107', 'CFDREG0':'108', 'LOG2BWEIGHT0':'109', 
       'PREAMPTAUA0':'110', 'PREAMPTAUB0':'111', 'POLYBUF':'112', 'U100':'192', 
       'DECIMATION':'256', 'REALTIMEA':'257', 'REALTIMEB':'258', 
       'REALTIMEC':'259', 'RUNTIMEA':'260', 'RUNTIMEB':'261', 'RUNTIMEC':'262', 
       'GSLTTIMEA':'263', 'GSLTTIMEB':'264', 'GSLTTIMEC':'265', 
       'NUMEVENTSA':'266', 'NUMEVENTSB':'267', 'NUMEVENTSC':'268', 
       'DSPERROR':'269', 'SYNCHDONE':'270', 'TEMPERATURE':'271', 'TEMP0':'272', 
       'BUFHEADLEN':'273', 'EVENTHEADLEN':'274', 'CHANHEADLEN':'275', 
       'U14':'276', 'USEROUT':'288', 'AOUTBUFFER':'304', 'LOUTBUFFER':'305', 
       'AECORR':'306', 'LECORR':'307', 'ATCORR':'308', 'LTCORR':'309', 
       'HARDWAREID':'310', 'HARDVARIANT':'311', 'FIFOLENGTH':'312', 
       'FIPPIID':'313', 'FIPPIVARIANT':'314', 'INTRFCID':'315', 
       'INTRFCVARIANT':'316', 'SOFTWAREID':'317', 'SOFTVARIANT':'318', 
       'LIVETIMEA0':'319', 'LIVETIMEB0':'320', 'LIVETIMEC0':'321', 
       'FASTPEAKSA0':'322', 'FASTPEAKSB0':'323', 'FASTPEAKSC0':'324', 
       'DEADTIMEA0':'325', 'DEADTIMEB0':'326', 'DEADTIMEC0':'327', 
       'COMPTONA0':'328', 'COMPTONB0':'329', 'COMPTONC0':'330', 
       'RAWCOMPTA0':'331', 'RAWCOMPTB0':'332', 'RAWCOMPTC0':'333', 
       'ADCPERDACA0':'334', 'ADCPERDACB0':'335', 'GAINFACTOR0':'336', 
       'UNUSEDC0':'339', 'U200':'343'}
  
  return d
