"""
Demonstrates configuring and reading a single analog input (AIN) with a LabJack.

"""
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

# Setup and call eWriteNames to configure AIN0 on the LabJack.
if deviceType == ljm.constants.dtT4:
    # LabJack T4 configuration

    # AIN0:
    #   Range: +/-10.0 V (10.0). Only AIN0-AIN3 support the +/-10 V range.
    #   Resolution index = Default (0)
    #   Settling, in microseconds = Auto (0)
    names = ["AIN0_RANGE", "AIN0_RESOLUTION_INDEX", "AIN0_SETTLING_US"]
    aValues = [10, 0, 0]
else:
    # LabJack T7 and other devices configuration

    # AIN0:
    #   Negative channel = single ended (199)
    #   Range: +/-10.0 V (10.0).
    #   Resolution index = Default (0)
    #   Settling, in microseconds = Auto (0)
    names = ["AIN0_NEGATIVE_CH", "AIN0_RANGE", "AIN0_RESOLUTION_INDEX", "AIN0_SETTLING_US"]
    aValues = [199, 10, 0, 0]
numFrames = len(names)
ljm.eWriteNames(handle, numFrames, names, aValues)

print("\nSet configuration:")
for i in range(numFrames):
    print("    %s : %f" % (names[i], aValues[i]))

# Setup and call eReadName to read AIN0 from the LabJack.
name = "AIN0"
result = ljm.eReadName(handle, name)

print("\n%s reading : %f V" % (name, result))

# Close handle
ljm.close(handle)
