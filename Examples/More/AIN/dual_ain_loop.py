"""
Demonstrates reading 2 analog inputs (AINs) in a loop from a LabJack.

"""
import sys
import time

from labjack import ljm


loopMessage = ""
if len(sys.argv) > 1:
    # An argument was passed. The first argument specifies how many times to
    # loop.
    try:
        loopAmount = int(sys.argv[1])
    except:
        raise Exception("Invalid first argument \"%s\". This specifies how many"
                        " times to loop and needs to be a number." %
                        str(sys.argv[1]))
else:
    # An argument was not passed. Loop an infinite amount of times.
    loopAmount = "infinite"
    loopMessage = " Press Ctrl+C to stop."

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

# Setup and call eWriteNames to configure AIN0 and AIN1 on the LabJack.
if deviceType == ljm.constants.dtT4:
    # LabJack T4 configuration

    # AIN0 and AIN1:
    #   Range: +/-10.0 V (10.0). Only AIN0-AIN3 support the +/-10 V range.
    #   Resolution index = Default (0)
    #   Settling, in microseconds = Auto (0)
    names = ["AIN0_RANGE", "AIN0_RESOLUTION_INDEX", "AIN0_SETTLING_US",
             "AIN1_RANGE", "AIN1_RESOLUTION_INDEX", "AIN1_SETTLING_US"]
    aValues = [10.0, 0, 0,
               10.0, 0, 0]
else:
    # LabJack T7 and other devices configuration

    # AIN0 and AIN1:
    #   Negative channel = single ended (199)
    #   Range: +/-10.0 V (10.0)
    #   Resolution index = Default (0)
    #   Settling, in microseconds = Auto (0)
    names = ["AIN0_NEGATIVE_CH", "AIN0_RANGE", "AIN0_RESOLUTION_INDEX", "AIN0_SETTLING_US",
             "AIN1_NEGATIVE_CH", "AIN1_RANGE", "AIN1_RESOLUTION_INDEX", "AIN1_SETTLING_US"]
    aValues = [199, 10.0, 0, 0,
               199, 10.0, 0, 0]
numFrames = len(names)
ljm.eWriteNames(handle, numFrames, names, aValues)

print("\nSet configuration:")
for i in range(numFrames):
    print("    %s : %f" % (names[i], aValues[i]))

# Read AIN0 and AIN1 from the LabJack with eReadNames in a loop.
numFrames = 2
names = ["AIN0", "AIN1"]

print("\nStarting %s read loops.%s\n" % (str(loopAmount), loopMessage))
intervalHandle = 1
ljm.startInterval(intervalHandle, 1000000)  # Delay between readings (in microseconds)
i = 0
while True:
    try:
        results = ljm.eReadNames(handle, numFrames, names)
        print("AIN0 : %f V, AIN1 : %f V" % (results[0], results[1]))
        ljm.waitForNextInterval(intervalHandle)
        if loopAmount is not "infinite":
            i = i + 1
            if i >= loopAmount:
                break
    except KeyboardInterrupt:
        break
    except Exception:
        import sys
        print(sys.exc_info()[1])
        break

# Close handles
ljm.cleanInterval(intervalHandle)
ljm.close(handle)
