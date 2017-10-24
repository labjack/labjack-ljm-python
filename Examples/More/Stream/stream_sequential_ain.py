"""
Demonstrates how to stream a range of sequential analog inputs using the eStream
functions. Useful when streaming many analog inputs. AIN channel scan list is
FIRST_AIN_CHANNEL to FIRST_AIN_CHANNEL + NUMBER_OF_AINS - 1.

"""
from datetime import datetime
import sys

from labjack import ljm


MAX_REQUESTS = 25  # The number of eStreamRead calls that will be performed.
FIRST_AIN_CHANNEL = 0  # 0 = AIN0
NUMBER_OF_AINS = 8

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

try:
    # When streaming, negative channels and ranges can be configured for
    # individual analog inputs, but the stream has only one settling time and
    # resolution.
    if deviceType == ljm.constants.dtT4:
        # T4 configuration

        # Configure the channels to analog input or digital I/O.
        # Update all digital I/O channels. b1 = Ignored. b0 = Affected.
        dioInhibit = 0x00000  # b00000000000000000000
        # Set AIN0-AIN3 and AIN FIRST_AIN_CHANNEL to
        # FIRST_AIN_CHANNEL+NUMBER_OF_AINS-1 as analog inputs (b1), the rest as
        # digital I/O (b0).
        dioAnalogEnable = (((2 ** NUMBER_OF_AINS) - 1) << FIRST_AIN_CHANNEL) | 0xF
        ljm.eWriteNames(handle, 2,
                        ["DIO_INHIBIT", "DIO_ANALOG_ENABLE"],
                        [dioInhibit, dioAnalogEnable])

        # Configure the analog input ranges.
        rangeAINHV = 10.0  # HV channels range (AIN0-AIN3)
        rangeAINLV = 2.5  # LV channels range (AIN4+)
        aNames = ["AIN%i_RANGE" % i for i in range(FIRST_AIN_CHANNEL, FIRST_AIN_CHANNEL + NUMBER_OF_AINS)]
        aValues = [rangeAINHV if i < 4 else rangeAINLV for i in range(FIRST_AIN_CHANNEL, FIRST_AIN_CHANNEL + NUMBER_OF_AINS)]
        ljm.eWriteNames(handle, len(aNames), aNames, aValues)

        # Configure the stream settling times and stream resolution index.
        aNames = ["STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX"]
        aValues = [0, 0]  # 0 (default), 0 (default)
        ljm.eWriteNames(handle, len(aNames), aNames, aValues)
    else:
        # T7 and other devices configuration

        # Ensure triggered stream is disabled.
        ljm.eWriteName(handle, "STREAM_TRIGGER_INDEX", 0)

        # Enabling internally-clocked stream.
        ljm.eWriteName(handle, "STREAM_CLOCK_SOURCE", 0)

        # Configure the analog input negative channels, ranges, stream settling
        # times and stream resolution index.
        aNames = ["AIN_ALL_NEGATIVE_CH", "AIN_ALL_RANGE", "STREAM_SETTLING_US",
                  "STREAM_RESOLUTION_INDEX"]
        aValues = [ljm.constants.GND, 10.0, 0, 0]  # single-ended, +/-10V, 0 (default), 0 (default)
        ljm.eWriteNames(handle, len(aNames), aNames, aValues)

    # Stream configuration
    aScanListNames = ["AIN%i" % i for i in range(FIRST_AIN_CHANNEL, FIRST_AIN_CHANNEL + NUMBER_OF_AINS)]  # Scan list names
    print("\nScan List = " + " ".join(aScanListNames))
    numAddresses = len(aScanListNames)
    aScanList = ljm.namesToAddresses(numAddresses, aScanListNames)[0]
    scanRate = 1000
    scansPerRead = int(scanRate / 2)

    # Configure and start stream
    scanRate = ljm.eStreamStart(handle, scansPerRead, numAddresses, aScanList, scanRate)
    print("\nStream started with a scan rate of %0.0f Hz." % scanRate)

    print("\nPerforming %i stream reads." % MAX_REQUESTS)
    start = datetime.now()
    totScans = 0
    totSkip = 0  # Total skipped samples

    i = 1
    while i <= MAX_REQUESTS:
        ret = ljm.eStreamRead(handle)

        aData = ret[0]
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
              "%i" % (curSkip / numAddresses, ret[1], ret[2]))
        i += 1

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
