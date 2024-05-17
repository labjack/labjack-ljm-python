"""
Demonstrates triggered stream on DIO0 / FIO0.
Note: The T4 is not supported for this example.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    NamesToAddresses:
        https://labjack.com/support/software/api/ljm/function-reference/utility/ljmnamestoaddresses
    eWriteNames:
        https://labjack.com/support/software/api/ljm/function-reference/ljmewritenames
    Single Value Functions (such as eWriteName and eReadName):
        https://labjack.com/support/software/api/ljm/function-reference/single-value-functions
    Library Configuration Functions (such as WriteLibraryConfigS):
        https://labjack.com/support/software/api/ljm/function-reference/library-configuration-functions
    Stream Functions (such as eStreamRead, eStreamStart and eStreamStop):
        https://labjack.com/support/software/api/ljm/function-reference/stream-functions

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Stream Mode:
        https://labjack.com/support/datasheets/t-series/communication/stream-mode
    Special Stream Modes (such as triggered):
        https://support.labjack.com/docs/3-2-2-special-stream-modes-t-series-datasheet
    Analog Inputs:
        https://labjack.com/support/datasheets/t-series/ain
    Digital I/O:
        https://labjack.com/support/datasheets/t-series/digital-io
    Extended DIO Features:
        https://labjack.com/support/datasheets/t-series/digital-io/extended-features
    Pulse Width In:
        https://labjack.com/support/datasheets/t-series/digital-io/extended-features/pulse-width

Note:
    Our Python interfaces throw exceptions when there are any issues with
    device communications that need addressed. Many of our examples will
    terminate immediately when an exception is thrown. The onus is on the API
    user to address the cause of any exceptions thrown, and add exception
    handling when appropriate. We create our own exception classes that are
    derived from the built-in Python Exception class and can be caught as such.
    For more information, see the implementation in our source code and the
    Python standard documentation.
"""
from datetime import datetime
import sys

from labjack import ljm

import ljm_stream_util


MAX_REQUESTS = 10  # The number of eStreamRead calls that will be performed.

# Open first found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
#handle = ljm.openS("T8", "ANY", "ANY")  # T8 device, Any connection, Any identifier
#handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
#handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

deviceType = info[0]

if deviceType == ljm.constants.dtT4:
    print("\nThe LabJack T4 does not support triggered stream.")
    sys.exit()

# Stream Configuration
aScanListNames = ["AIN0", "AIN1"]  # Scan list names to stream
numAddresses = len(aScanListNames)
aScanList = ljm.namesToAddresses(numAddresses, aScanListNames)[0]
scanRate = 1000
scansPerRead = int(scanRate / 2)

TRIGGER_NAME = "DIO0"


def configureDeviceForTriggeredStream(handle, triggerName):
    """Configure the device to wait for a trigger before beginning stream.

    @para handle: The device handle
    @type handle: int
    @para triggerName: The name of the channel that will trigger stream to start
    @type triggerName: str
    """
    address = ljm.nameToAddress(triggerName)[0]
    ljm.eWriteName(handle, "STREAM_TRIGGER_INDEX", address)

    # Clear any previous settings on triggerName's Extended Feature registers
    ljm.eWriteName(handle, "%s_EF_ENABLE" % triggerName, 0)

    # 5 enables a rising or falling edge to trigger stream
    ljm.eWriteName(handle, "%s_EF_INDEX" % triggerName, 5)

    # Enable
    ljm.eWriteName(handle, "%s_EF_ENABLE" % triggerName, 1)


def configureLJMForTriggeredStream():
    ljm.writeLibraryConfigS(ljm.constants.STREAM_SCANS_RETURN, ljm.constants.STREAM_SCANS_RETURN_ALL_OR_NONE)
    ljm.writeLibraryConfigS(ljm.constants.STREAM_RECEIVE_TIMEOUT_MS, 0)
    # By default, LJM will time out with an error while waiting for the stream
    # trigger to occur.


try:
    # When streaming, negative channels and ranges can be configured for
    # individual analog inputs, but the stream has only one settling time and
    # resolution.

    # Ensure triggered stream is disabled.
    ljm.eWriteName(handle, "STREAM_TRIGGER_INDEX", 0)

    # Enabling internally-clocked stream.
    ljm.eWriteName(handle, "STREAM_CLOCK_SOURCE", 0)

    # AIN0 and AIN1 ranges are +/-10 V (T7) or +/-11 V (T8).
    # Stream resolution index is 0 (default).
    aNames = ["AIN0_RANGE", "AIN1_RANGE", "STREAM_RESOLUTION_INDEX"]
    aValues = [10.0, 10.0, 0]

    # Negative channel and settling configurations do not apply to the T8
    if deviceType == ljm.constants.dtT7:
        #     Negative Channel = 199 (Single-ended)
        #     Settling = 0 (auto)
        aNames.extend(["AIN0_NEGATIVE_CH", "STREAM_SETTLING_US",
                       "AIN1_NEGATIVE_CH"])
        aValues.extend([199, 0, 199])

    # Write the analog inputs' negative channels, ranges, stream settling time
    # and stream resolution configuration.
    numFrames = len(aNames)
    ljm.eWriteNames(handle, numFrames, aNames, aValues)

    configureDeviceForTriggeredStream(handle, TRIGGER_NAME)
    configureLJMForTriggeredStream()

    # Configure and start stream
    scanRate = ljm.eStreamStart(handle, scansPerRead, numAddresses, aScanList, scanRate)
    print("\nStream started with a scan rate of %0.0f Hz." % scanRate)

    print("\nPerforming %i stream reads." % MAX_REQUESTS)
    start = datetime.now()
    totScans = 0
    totSkip = 0  # Total skipped samples

    i = 1
    ljmScanBacklog = 0
    while i <= MAX_REQUESTS:
        ljm_stream_util.variableStreamSleep(scansPerRead, scanRate, ljmScanBacklog)

        try:
            ret = ljm.eStreamRead(handle)

            aData = ret[0]
            ljmScanBacklog = ret[2]
            scans = len(aData) / numAddresses
            totScans += scans

            # Count the skipped samples which are indicated by -9999 values. Missed
            # samples occur after a device's stream buffer overflows and are
            # reported after auto-recover mode ends.
            curSkip = aData.count(-9999.0)
            totSkip += curSkip

            print("\neStreamRead %i" % i)
            ainStr = ""
            for j in range(0, numAddresses):
                ainStr += "%s = %0.5f, " % (aScanListNames[j], aData[j])
            print("  1st scan out of %i: %s" % (scans, ainStr))
            print("  Scans Skipped = %0.0f, Scan Backlogs: Device = %i, LJM = "
                  "%i" % (curSkip/numAddresses, ret[1], ljmScanBacklog))
            i += 1
        except ljm.LJMError as err:
            if err.errorCode == ljm.errorcodes.NO_SCANS_RETURNED:
                sys.stdout.write('.')
                sys.stdout.flush()
                continue
            else:
                raise err

    end = datetime.now()

    print("\nTotal scans = %i" % (totScans))
    tt = (end - start).seconds + float((end - start).microseconds) / 1000000
    print("Time taken = %f seconds" % (tt))
    print("LJM Scan Rate = %f scans/second" % (scanRate))
    print("Timed Scan Rate = %f scans/second" % (totScans / tt))
    print("Timed Sample Rate = %f samples/second" % (totScans * numAddresses / tt))
    print("Skipped scans = %0.0f" % (totSkip / numAddresses))
except ljm.LJMError:
    ljme = sys.exc_info()[1]
    print(ljme)
except Exception:
    e = sys.exc_info()[1]
    print(e)

try:
    print("\nStop Stream")
    ljm.eStreamStop(handle)
except ljm.LJMError:
    ljme = sys.exc_info()[1]
    print(ljme)
except Exception:
    e = sys.exc_info()[1]
    print(e)

# Close handle
ljm.close(handle)
