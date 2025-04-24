"""
Demonstrates triggered stream on DIO0 / FIO0.
Note: The T4 is not supported.

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
    eWriteName:
        https://labjack.com/support/software/api/ljm/function-reference/ljmewritename
    eWriteNames:
        https://labjack.com/support/software/api/ljm/function-reference/ljmewritenames
    Library Configuration Functions (such as WriteLibraryConfigS):
        https://labjack.com/support/software/api/ljm/function-reference/library-configuration-functions
    Stream Functions (such as eStreamStart, eStreamRead and eStreamStop):
        https://labjack.com/support/software/api/ljm/function-reference/stream-functions

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Stream Mode:
        https://labjack.com/support/datasheets/t-series/communication/stream-mode
    Special Stream Modes (such as triggered stream):
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
import sys
import time

from labjack import ljm


def variableStreamSleep(scansPerRead, scanRate, LJMScanBacklog):
    """
    Sleeps for approximately the expected amount of time until the next
    scan is ready to be read.

    Args:
        scansPerRead: The number of scans returned by a eStreamRead call.
        scanRate: The stream scan rate.
        LJMScanBacklog: The number of backlogged scans in the LJM buffer.

    """
    DECREASE_TOTAL = 0.9
    sleepFactor = 0.0  # Default sleep factor.
    portionScansReady = float(LJMScanBacklog) / scansPerRead
    if (portionScansReady <= DECREASE_TOTAL):
        sleepFactor = (1 - portionScansReady) * DECREASE_TOTAL
    sleepTime = sleepFactor * scansPerRead / float(scanRate)
    time.sleep(sleepTime)


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

try:
    # When streaming, negative channels and ranges can be configured for
    # individual analog inputs, but the stream has only one settling time and
    # resolution.

    # Ensure triggered stream is disabled. Will enable later.
    ljm.eWriteName(handle, "STREAM_TRIGGER_INDEX", 0)

    # Enabling internally-clocked stream.
    ljm.eWriteName(handle, "STREAM_CLOCK_SOURCE", 0)

    # AIN0 and AIN1 ranges are +/-10 V (T7) or +/-11 V (T8).
    # Stream resolution index is 0 (default).
    aNames = ["AIN0_RANGE", "AIN1_RANGE", "STREAM_RESOLUTION_INDEX"]
    aValues = [10.0, 10.0, 0]

    # Negative channel and settling configurations do not apply to the T8.
    if deviceType == ljm.constants.dtT7:
        #     Negative Channel = 199 (Single-ended)
        #     Settling = 0 (auto)
        aNames.extend(["AIN0_NEGATIVE_CH", "AIN1_NEGATIVE_CH",
                       "STREAM_SETTLING_US"])
        aValues.extend([199, 199, 0])

    # Write the analog inputs' negative channels, ranges, stream settling time
    # and stream resolution configuration.
    numFrames = len(aNames)
    ljm.eWriteNames(handle, numFrames, aNames, aValues)

    # Configure the stream trigger and related extended feature settings.

    # Set the stream trigger index to DIO0.
    # Note that the register address needs to be set for the index.
    triggerName = "DIO0"
    address = ljm.nameToAddress(triggerName)[0]
    ljm.eWriteName(handle, "STREAM_TRIGGER_INDEX", address)

    # Disable the DIO0 extended feature.
    ljm.eWriteName(handle, "%s_EF_ENABLE" % triggerName, 0)

    # Configure DIO0 extended feature.
    # Set to Pulse Width In (index 5) for a rising or falling edge to
    # trigger the stream.
    ljm.eWriteName(handle, "%s_EF_INDEX" % triggerName, 5)

    # Enable the DIO0 extended feature.
    ljm.eWriteName(handle, "%s_EF_ENABLE" % triggerName, 1)

    # Configure LJM stream settings to handle stream trigger timing.

    # Set STREAM_SCANS_RETURN to STREAM_SCANS_RETURN_ALL_OR_NONE.
    # This will make eStreamRead return scansPerRead amount of scans if all
    # are available, or no scans if not.
    ljm.writeLibraryConfigS(ljm.constants.STREAM_SCANS_RETURN, ljm.constants.STREAM_SCANS_RETURN_ALL_OR_NONE)

    # Set the STREAM_RECEIVE_TIMEOUT_MS to 0 for infinite timeout.
    # By default, LJM will timeout with an error while waiting for the stream
    # trigger to occur.
    ljm.writeLibraryConfigS(ljm.constants.STREAM_RECEIVE_TIMEOUT_MS, 0)

    # Stream settings.
    aScanListNames = ["AIN0", "AIN1"]  # Scan list names to stream.
    numAddresses = len(aScanListNames)
    # Scan list register addresses converted from the names. The scan list
    # needs to be register addresses.
    aScanList = ljm.namesToAddresses(numAddresses, aScanListNames)[0]
    scanRate = 1000  # Scan rate set to 1000 Hz.
    scansPerRead = int(scanRate / 2)  # Scans per read set half of scan rate.

    # Configure and start the stream.
    scanRate = ljm.eStreamStart(handle, scansPerRead, numAddresses, aScanList, scanRate)
    print("\nStream started with a scan rate of %0.0f Hz." % scanRate)

    # Read the stream data in a loop.
    maxRequests = 10  # The number of eStreamRead calls with data that will be
                      # performed.
    print("\nPerforming %i stream reads." % maxRequests)
    totScans = 0  # Total amount of scans.
    totSkip = 0  # Total amount of skipped samples.
    i = 1  # Keeps track of the amount of eStreamRead calls with data.
    ljmScanBacklog = 0  # Stores the latest ljmScanBacklog from the
                        # eStreamRead call.
    while i <= maxRequests:
        # Sleep based on scansPerRead, scanRate and last ljmScanBacklog.
        variableStreamSleep(scansPerRead, scanRate, ljmScanBacklog)

        try:
            # Read the stream data (all or none configured).
            ret = ljm.eStreamRead(handle)

            aData = ret[0]
            deviceScanBacklog = ret[1]
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
            print("  Scans Skipped = %0.0f, Scan Backlogs: Device = %i, LJM = %i"
                  % (curSkip/numAddresses, deviceScanBacklog, ljmScanBacklog))
            i += 1
        except ljm.LJMError as err:
            if err.errorCode == ljm.errorcodes.NO_SCANS_RETURNED:
                # No scans returned. Continue the loop and disregard the read.
                sys.stdout.write('.')
                sys.stdout.flush()
                continue
            else:
                # Other error. Raising an exception which will stop the stream
                # reads.
                raise err

    # Streaming done. Display post streaming information.
    print("\nTotal scans = %i" % (totScans))
    print("LJM Scan Rate = %f scans/second" % (scanRate))
    print("Skipped scans = %0.0f" % (totSkip / numAddresses))
except ljm.LJMError:
    ljme = sys.exc_info()[1]
    print(ljme)
except Exception:
    e = sys.exc_info()[1]
    print(e)

try:
    # Stop streaming.
    print("\nStop Stream")
    ljm.eStreamStop(handle)
except ljm.LJMError:
    ljme = sys.exc_info()[1]
    print(ljme)
except Exception:
    e = sys.exc_info()[1]
    print(e)

# Close the handle.
ljm.close(handle)
