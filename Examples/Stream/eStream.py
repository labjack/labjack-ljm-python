"""
Demonstrates how to stream using the eStream functions.

"""

from labjack import ljm
import time
import sys
from datetime import datetime

#ljm.writeLibraryConfigS(ljm.constants.LOG_LEVEL, 1); # 1 is stream packets, 2 is trace log level
#ljm.writeLibraryConfigS(ljm.constants.LOG_MODE, 2); # 2 is continuous log, 3 is log on error

# Open first found LabJack
#handle = ljm.open(ljm.constants.ANY, ljm.constants.ANY, "ANY")
#handle = ljm.openS("ANY", "ETHERNET", "192.168.1.192")
handle = ljm.openS("ANY", "USB", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

#Stream Configuration
aScanListNames = ["AIN0", "AIN1"] #Scan list names to stream
numAddresses = len(aScanListNames)
aScanList = ljm.namesToAddresses(numAddresses, aScanListNames)[0]
scansPerRead = int(2000/numAddresses)
scanRate = 5000

#Configure scan list for single ended readings
aNames = [s+"_NEGATIVE_CH" for s in aScanListNames] #AINX_NEGATIVE_CH
ljm.eWriteNames(handle, numAddresses, aNames, [199]*numAddresses)

try:
    #Configure and start stream
    scanRate = ljm.eStreamStart(handle, scansPerRead, numAddresses, aScanList, scanRate)
    print("Start Stream")
    
    print("Start Read")
    loop = 50
    start = datetime.now()
    totScans = 0
    totSkip = 0 #Total skipped samples
    for i in range(loop):
        ret = ljm.eStreamRead(handle)
        
        data = ret[0]
        scans = len(data)/numAddresses
        totScans += scans
        
        #Count the skipped samples which are indicated by -9999 values. Missed
        #samples occur after a device's stream buffer overflows and are reported
        #after auto-recover mode ends.
        curSkip = data.count(-9999.0)
        totSkip += curSkip
        
        #Display every 5 eStreamRead calls or when skipped scans are detected
        if (i+1) % 5 == 0 or curSkip > 0:
            print("\neStreamRead %i" % (i+1))
            ainStr = ""
            for i in range(0, numAddresses):
                ainStr += "%s = %0.5f " % (aScanListNames[i], data[i])
            print("  1st scan out of %i: %s" % (scans, ainStr))
            print("  Scans Skipped = %0.0f, Scan Backlogs: Device = %i, LJM = " \
                  "%i" % (curSkip/numAddresses, ret[1], ret[2]))

    end = datetime.now()

    print("\nTotal scans = %i" % (totScans))
    tt = (end-start).seconds + float((end-start).microseconds)/1000000
    print("Time taken = %f seconds" % (tt))
    print("LJM Scan Rate = %f scans/second" % (scanRate))
    print("Timed Scan Rate = %f scans/second" % (totScans/tt))
    print("Sample Rate = %f samples/second" % (totScans*numAddresses/tt))
    print("Skipped scans = %0.0f" % (totSkip/numAddresses))
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
