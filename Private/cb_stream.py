"""
Demonstrates how to stream using the eStream functions.
"""
from labjack import ljm
import time
import sys
from datetime import datetime
import traceback

#Class to hold our stream information
class StreamInfo:
    def __init__(self):
        self.handle = 0
        self.scanRate = 0
        self.scansPerRead = 0
        self.streamLengthMS = 0
        self.done = 0
        
        self.numAddresses = 0
        self.aScanList = 0
        self.aScanListNames = 0
        
        self.aDataSize = 0
        self.aData = 0

        self.streamRead = 0
        self.totSkip = 0
        self.totScans = 0

        self.argInner = None
        self.arg = None
        self.callback = None


#Function to pass to the callback function
def myStreamReadCallback(arg):
    global si

    if si.handle != arg:
        print("myStreamReadCallback - Unexpected argument: %d" % (arg))
        return

    # Check if stream is done so that we don't output the print statement below
    if si.done:
        return

    print("\niteration: % 3d    " % (si.streamRead))
    si.streamRead += 1

    try:
        ret = ljm.eStreamRead(si.handle)
        aData = ret[0]
        deviceScanBacklog = ret[1]
        ljmScanBackLog = ret[2]

        scans = len(aData) / si.numAddresses
        si.totScans += scans

        # Count the skipped samples which are indicated by -9999 values. Missed
        # samples occur after a device's stream buffer overflows and are
        # reported after auto-recover mode ends.
        curSkip = aData.count(-9999.0)
        si.totSkip += curSkip

        ainStr = ""
        for j in range(0, si.numAddresses):
            ainStr += "%s = %0.5f, " % (si.aScanListNames[j], aData[j])
        print("  1st scan out of %i: %s" % (scans, ainStr))
        print("  Scans Skipped = %0.0f, Scan Backlogs: Device = %i, LJM = "
              "%i" % (curSkip/si.numAddresses, deviceScanBacklog, ljmScanBackLog))

    # If LJM has called this callback, the data is valid, but LJM_eStreamRead
    # may return LJME_STREAM_NOT_RUNNING if another thread (such as the Python
    # main thread) has stopped stream.
    except ljm.LJMError as err:
        if err.errorCode == ljm.errorcodes.STREAM_NOT_RUNNING:
            print("eStreamRead returned LJME_STREAM_NOT_RUNNING.")
        else:
            ljm.eStreamStop(si.handle)


#Main code
si = StreamInfo()

# Open first found LabJack
si.handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctUSB, "ANY")
#handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(si.handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Stream Configuration
si.aScanListNames = ["AIN0",  "FIO_STATE",  "SYSTEM_TIMER_20HZ", "STREAM_DATA_CAPTURE_16"] #Scan list names to stream
si.scanRate = 2000
si.scansPerRead = si.scanRate/2
si.streamLengthMS = 5000
si.done = False
si.numAddresses = len(si.aScanListNames)
si.aScanList = ljm.namesToAddresses(si.numAddresses, si.aScanListNames)[0]
si.aDataSize - si.numAddresses * si.scansPerRead


try:
    t0 = datetime.now()

    # Configure and start stream
    scanRate = si.scanRate
    try:
        scanRate = ljm.eStreamStart(si.handle, si.scansPerRead, si.numAddresses, si.aScanList, si.scanRate)
    except ljm.LJMError as excep:
        if excep.errorCode == ljm.errorcodes.USING_DEFAULT_CALIBRATION:
            print("Warning: Using default calibration:")
            print("  - It's possible device recently booted or the device calibration is incorrect.")
            print("  - Consider using Kipling to check the device calibration constants.")
        else:
            raise
    si.scanRate = scanRate #Actual scan rate
    print("\nStream started with a scan rate of %0.0f Hz." % si.scanRate)

    ljm.setStreamCallback(si.handle, myStreamReadCallback)

    print("Stream running, callback set, sleeping for " + str(si.streamLengthMS) + " milliseconds\n", )
    time.sleep(si.streamLengthMS/1000.0)
except ljm.LJMError:
    
    #TODO: FIGURE OUT HOW TO PRINT THE STACKTRACE
    ljme = sys.exc_info()[1]
    st = sys.exc_info()[2]
    #print("LJM Exception: " + str(ljme))
    print("\nLJM Exception:\n" + "".join(i for i in traceback.format_exc()))
    #print(st)
    #traceback.print_stack()

except Exception:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    print("\nException:\n" + "".join('  ' + i for i in lines))
    #or
    """
    print("\nException:\n" + str(traceback.format_exc()))
    #or
    e = sys.exc_info()[1]
    st = sys.exc_info()[2]
    print("\nException:\n" + "".join(i for i in traceback.format_exc()))
    """
    
print("\nStopping Stream...")
si.done = True
ljm.eStreamStop(si.handle)
t1 = datetime.now()

print("Stream stopped. " + str((t1-t0).seconds*1000 + float((t1-t0).microseconds)/1000) + " milliseconds have elapsed since eStreamStart\n")

# Close handle
ljm.close(si.handle)
