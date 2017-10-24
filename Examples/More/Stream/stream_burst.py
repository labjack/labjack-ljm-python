"""
Demonstrates how to use the streamBurst function for streaming.

"""
from datetime import datetime
import sys

from labjack import ljm


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
aScanListNames = ["AIN0", "AIN1"]  # Scan list names to stream
numAddresses = len(aScanListNames)
aScanList = ljm.namesToAddresses(numAddresses, aScanListNames)[0]  # Scan list addresses for streamBurst
scanRate = 10000  # Scans per second
numScans = 20000  # Number of scans to perform

try:
    # When streaming, negative channels and ranges can be configured for
    # individual analog inputs, but the stream has only one settling time and
    # resolution.

    if deviceType == ljm.constants.dtT4:
        # LabJack T4 configuration

        # AIN0 and AIN1 ranges are +/-10 V, stream settling is 0 (default) and
        # stream resolution index is 0 (default).
        aNames = ["AIN0_RANGE", "AIN1_RANGE", "STREAM_SETTLING_US",
                  "STREAM_RESOLUTION_INDEX"]
        aValues = [10.0, 10.0, 0, 0]
    else:
        # LabJack T7 and other devices configuration

        # Ensure triggered stream is disabled.
        ljm.eWriteName(handle, "STREAM_TRIGGER_INDEX", 0)

        # Enabling internally-clocked stream.
        ljm.eWriteName(handle, "STREAM_CLOCK_SOURCE", 0)

        # All negative channels are single-ended, AIN0 and AIN1 ranges are
        # +/-10 V, stream settling is 0 (default) and stream resolution index
        # is 0 (default).
        aNames = ["AIN_ALL_NEGATIVE_CH", "AIN0_RANGE", "AIN1_RANGE",
                  "STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX"]
        aValues = [ljm.constants.GND, 10.0, 10.0, 0, 0]
    # Write the analog inputs' negative channels (when applicable), ranges,
    # stream settling time and stream resolution configuration.
    numFrames = len(aNames)
    ljm.eWriteNames(handle, numFrames, aNames, aValues)

    print("\nScan list:")
    for chan in aScanListNames:
        print("  %s" % chan)
    print("Scan rate = %s Hz" % scanRate)
    print("Sample rate = %s Hz" % (scanRate * numAddresses))
    print("Total number of scans: %s" % numScans)
    print("Total number of samples: %s" % (numScans * numAddresses))
    print("Seconds of samples = %s" % (numScans / scanRate))

    print("\nStreaming with streamBurst ...")
    start = datetime.now()
    scanRate, aData = ljm.streamBurst(handle, numAddresses, aScanList, scanRate, numScans)
    end = datetime.now()
    print("Done")

    skipped = aData.count(-9999.0)
    print("\nSkipped scans = %0.0f" % (skipped / numAddresses))
    tt = (end - start).seconds + float((end - start).microseconds) / 1000000
    print("Time taken = %f seconds" % (tt))

    ainStr1 = ""
    ainStr2 = ""
    lastScanIndex = len(aData) - numAddresses
    for j in range(0, numAddresses):
        ainStr1 += "%s = %0.5f, " % (aScanListNames[j], aData[j])
        ainStr2 += "%s = %0.5f, " % (aScanListNames[j], aData[lastScanIndex + j])
    print("\nFirst scan: %s" % ainStr1)
    print("Last scan: %s" % ainStr2)
except ljm.LJMError:
    ljme = sys.exc_info()[1]
    print(ljme)
except Exception:
    e = sys.exc_info()[1]
    print(e)

# Close handle
ljm.close(handle)
