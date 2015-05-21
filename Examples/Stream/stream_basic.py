"""
Demonstrates how to stream using the eStream functions.

"""

from labjack import ljm
import time
import sys
from datetime import datetime

MAX_REQUESTS = 50 # The number of eStreamRead calls that will be performed.

# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
#handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Stream Configuration
aScanListNames = ["AIN0", "AIN1", "AIN2", "AIN3"] #Scan list names to stream
numAddresses = len(aScanListNames)
aScanList = ljm.namesToAddresses(numAddresses, aScanListNames)[0]
scanRate = 1000
scansPerRead = int(scanRate/2)

try:
    # Configure the analog inputs' negative channel, range, settling time and
    # resolution.
    # Note when streaming, negative channels and ranges can be configured for
    # individual analog inputs, but the stream has only one settling time and
    # resolution.
    aNames = ["AIN_ALL_NEGATIVE_CH", "AIN_ALL_RANGE", "STREAM_SETTLING_US",
              "STREAM_RESOLUTION_INDEX"]
    aValues = [ljm.constants.GND, 10.0, 0, 0] #single-ended, +/-10V, 0 (default),
                                              #0 (default)
    ljm.eWriteNames(handle, len(aNames), aNames, aValues)

    # Configure and start stream
    scanRate = ljm.eStreamStart(handle, scansPerRead, numAddresses, aScanList, scanRate)
    print("\nStream started with a scan rate of %0.0f Hz." % scanRate)

    print("\nPerforming %i stream reads." % MAX_REQUESTS)
    start = datetime.now()
    totScans = 0
    totSkip = 0 # Total skipped samples

    i = 1
    while i <= MAX_REQUESTS:
        ret = ljm.eStreamRead(handle)
        
        data = ret[0]
        scans = len(data)/numAddresses
        totScans += scans
        
        # Count the skipped samples which are indicated by -9999 values. Missed
        # samples occur after a device's stream buffer overflows and are
        # reported after auto-recover mode ends.
        curSkip = data.count(-9999.0)
        totSkip += curSkip
        
        print("\neStreamRead %i" % i)
        ainStr = ""
        for j in range(0, numAddresses):
            ainStr += "%s = %0.5f " % (aScanListNames[j], data[j])
        print("  1st scan out of %i: %s" % (scans, ainStr))
        print("  Scans Skipped = %0.0f, Scan Backlogs: Device = %i, LJM = " \
              "%i" % (curSkip/numAddresses, ret[1], ret[2]))
        i += 1

    end = datetime.now()

    print("\nTotal scans = %i" % (totScans))
    tt = (end-start).seconds + float((end-start).microseconds)/1000000
    print("Time taken = %f seconds" % (tt))
    print("LJM Scan Rate = %f scans/second" % (scanRate))
    print("Timed Scan Rate = %f scans/second" % (totScans/tt))
    print("Timed Sample Rate = %f samples/second" % (totScans*numAddresses/tt))
    print("Skipped scans = %0.0f" % (totSkip/numAddresses))
except ljm.LJMError:
    ljme = sys.exc_info()[1]
    print(ljme)
except Exception:
    e = sys.exc_info()[1]
    print(e)

print("\nStop Stream")
ljm.eStreamStop(handle)

# Close handle
ljm.close(handle)
