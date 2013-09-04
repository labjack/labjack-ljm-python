"""
Demonstrates how to stream using the eStream functions.

"""

from labjack import ljm
import time
import sys
from datetime import datetime

ljm.writeLibraryConfigS(ljm.constants.LOG_LEVEL, 1); # 1 is stream packets, 2 is trace log level
ljm.writeLibraryConfigS(ljm.constants.LOG_MODE, 2); # 2 is continuous log, 3 is log on error

# Open first found LabJack
#handle = ljm.open(ljm.constants.dtT7, ljm.constants.ctETHERNET, "192.168.1.175")
#handle = ljm.openS("ANY", "ETHERNET", "192.168.1.192")
handle = ljm.openS("ANY", "USB", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

numAddresses = 2
scansPerRead = int(252/numAddresses) #252 is the max reliable # samples per packet
aScanList = [0, 2] #[AIN0, AIN1]
#aScanList_Neg = [ljm.constants.GND, ljm.constants.GND]
scanRate = 15000

#unknown error
#numAddresses = 2
#scansPerRead = int(252/numAddresses) #252 is the max reliable # samples per packet
#aScanList = [0, 2] #[AIN0, AIN1]
##aScanList_Neg = [ljm.constants.GND, ljm.constants.GND]
#scanRate = 50000

scanRate = ljm.eStreamStart(handle, scansPerRead, numAddresses, aScanList, scanRate)
print("Start Stream")

print("Start Read")
try:
    loop = 1000
    start = datetime.now()
    totScans = 0
    for i in range(loop):
        ret = ljm.eStreamRead(handle)
        data = ret[0]
        scans = len(data)/numAddresses
        totScans += scans
        #figure out the missing scans
        #totScans -= ret[1]
        print("\neStreamRead %i" % (i+1))
        print("  First scan out of %i: AIN0 = %f, AIN1 = %f" % \
              (scans, data[0], data[1]))
        print("  numSkippedScans: %i, deviceScanBacklog: %i, ljmScanBacklog: " \
              "%i" % (0, ret[1], ret[2])) #fix num skipped scans
    end = datetime.now()

    print("\nTotal scans: %i" % (totScans))
    time = (end-start).seconds + float((end-start).microseconds)/1000000
    print("Time taken: %f seconds" % (time))
    print("LJM Scan Rate: %f scans/second" % (scanRate))
    print("Timed Scan Rate: %f scans/second" % (totScans/time))
    print("Sample Rate: %f samples/second" % (totScans*numAddresses/time))
except ljm.LJMError:
    ljme = sys.exc_info()[1]
    print(ljme)
except Exception:
    e = sys.exc_info()[1]
    print(e)

print("Stop Stream")
ljm.eStreamStop(handle)

# Close handle
ljm.close(handle)
