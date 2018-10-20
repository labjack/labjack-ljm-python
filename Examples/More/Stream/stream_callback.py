"""
Demonstrates how to stream using a callback to read stream, which is useful
for streaming in external clock stream mode.

"""
from datetime import datetime
import sys
import threading
import time
import traceback

from labjack import ljm


# Class to hold our stream information
class StreamInfo:
    def __init__(self):
        self.handle = 0
        self.scanRate = 0
        self.scansPerRead = 0
        self.streamLengthMS = 0
        self.done = False

        self.numAddresses = 0
        self.aScanList = 0
        self.aScanListNames = 0
        
        self.aDataSize = 0
        self.aData = None

        self.streamRead = 0
        self.totSkip = 0
        self.totScans = 0


printLock = threading.Lock()
def printWithLock(string):
    global printLock
    with printLock:
        print(string)


# Function to pass to the callback function. This needs have one
# parameter/argument, which will be the handle.
def myStreamReadCallback(arg):
    global si

    if si.handle != arg:
        printWithLock("myStreamReadCallback - Unexpected argument: %d" % (arg))
        return

    # Check if stream is done so that we don't output the print statement below.
    if si.done:
        return

    string = "\niteration: %3d\n" % si.streamRead
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

        string += "  1st scan out of %i: " % scans
        for j in range(0, si.numAddresses):
            string += "%s = %0.5f, " % (si.aScanListNames[j], aData[j])
        string += "\n  Scans Skipped = %0.0f, Scan Backlogs: Device = %i, LJM = %i" % \
                (curSkip/si.numAddresses, deviceScanBacklog, ljmScanBackLog)
        printWithLock(string)

    # If LJM has called this callback, the data is valid, but LJM_eStreamRead
    # may return LJME_STREAM_NOT_RUNNING if another thread (such as the Python
    # main thread) has stopped stream.
    except ljm.LJMError as err:
        if err.errorCode == ljm.errorcodes.STREAM_NOT_RUNNING:
            printWithLock("eStreamRead returned LJME_STREAM_NOT_RUNNING.")
        else:
            printWithLock(err)

# Create the global StreamInfo class which is used to pass information between
# the callback and main code.
si = StreamInfo()


if __name__ == "__main__":
    # Open first found LabJack
    handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
    #handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
    #handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
    #handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

    info = ljm.getHandleInfo(handle)
    print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
          "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
          (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

    deviceType = info[0]

    # Stream Configuration
    si.aScanListNames = ["AIN0", "FIO_STATE", "SYSTEM_TIMER_20HZ",
                         "STREAM_DATA_CAPTURE_16"]  # Scan list names to stream
    si.numAddresses = len(si.aScanListNames)
    si.aScanList = ljm.namesToAddresses(si.numAddresses, si.aScanListNames)[0]
    si.scanRate = 2000
    si.scansPerRead = int(si.scanRate / 2)

    si.streamLengthMS = 10000
    si.done = False
    si.aDataSize - si.numAddresses * si.scansPerRead
    si.handle = handle

    try:
        # When streaming, negative channels and ranges can be configured for
        # individual analog inputs, but the stream has only one settling time
        # and resolution.

        if deviceType == ljm.constants.dtT4:
            # LabJack T4 configuration

            # AIN0 range is +/-10 V, stream settling is 0 (default) and stream
            # stream resolution index is 0 (default).
            aNames = ["AIN0_RANGE", "STREAM_SETTLING_US",
                      "STREAM_RESOLUTION_INDEX"]
            aValues = [10.0, 0, 0]
        else:
            # LabJack T7 and other devices configuration

            # Ensure triggered stream is disabled.
            ljm.eWriteName(handle, "STREAM_TRIGGER_INDEX", 0)

            # Enabling internally-clocked stream.
            ljm.eWriteName(handle, "STREAM_CLOCK_SOURCE", 0)

            # All negative channels are single-ended, AIN0 range is +/-10 V,
            # stream settling is 0 (default) and stream resolution index
            # is 0 (default).
            aNames = ["AIN_ALL_NEGATIVE_CH", "AIN0_RANGE",
                      "STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX"]
            aValues = [ljm.constants.GND, 10.0, 0, 0]
        # Write the analog inputs' negative channels (when applicable), ranges,
        # stream settling time and stream resolution configuration.
        numFrames = len(aNames)
        ljm.eWriteNames(handle, numFrames, aNames, aValues)

        t0 = datetime.now()

        # Configure and start stream
        si.scanRate = ljm.eStreamStart(handle, si.scansPerRead, si.numAddresses, si.aScanList, si.scanRate)
        print("\nStream started with a scan rate of %0.0f Hz." % si.scanRate)

        # Set the callback function.
        ljm.setStreamCallback(handle, myStreamReadCallback)

        printWithLock("Stream running, callback set, sleeping for %i milliseconds." % si.streamLengthMS)
        time.sleep(si.streamLengthMS/1000.0)

        si.done = True
        t1 = datetime.now()

        printWithLock("\nStreaming done. %.3f milliseconds have elapsed since eStreamStart" %
              ((t1-t0).seconds*1000 + float((t1-t0).microseconds)/1000))
    except ljm.LJMError:
        ljme = sys.exc_info()[1]
        printWithLock(ljme)
    except Exception:
        e = sys.exc_info()[1]
        printWithLock(e)

    try:
        printWithLock("\nStop Stream")
        si.done = True
        ljm.eStreamStop(handle)
    except ljm.LJMError:
        ljme = sys.exc_info()[1]
        print(ljme)
    except Exception:
        e = sys.exc_info()[1]
        print(e)

    # Close handle
    ljm.close(handle)
