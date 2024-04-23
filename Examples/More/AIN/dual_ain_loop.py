"""
Demonstrates reading 2 analog inputs (AINs) in a loop from a LabJack.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    Multiple Value Functions (such as eWriteNames and eReadNames):
        https://labjack.com/support/software/api/ljm/function-reference/multiple-value-functions
    Timing Functions (such as StartInterval, WaitForNextInterval and CleanInterval):
        https://labjack.com/support/software/api/ljm/function-reference/timing-functions

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Analog Inputs:
        https://labjack.com/support/datasheets/t-series/ain

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
#handle = ljm.openS("T8", "ANY", "ANY")  # T8 device, Any connection, Any identifier
#handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
#handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
#handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

deviceType = info[0]

# Setup and call eWriteNames to configure AIN0 and AIN1 on the LabJack.
if deviceType == ljm.constants.dtT8:
    # LabJack T8 configuration
    
    # AIN0 and AIN1:
    #   Range = +/-11 V (11)
    # AIN all resolution index = Default (0)
    # AIN sampling rate, in Hz = Auto (0)
    aNames = ["AIN0_RANGE", "AIN1_RANGE",
              "AIN_ALL_RESOLUTION_INDEX", "AIN_SAMPLING_RATE_HZ"]
    aValues = [11, 11,
               0, 0]
elif deviceType == ljm.constants.dtT4:
    # LabJack T4 configuration

    # AIN0 and AIN1:
    #   Resolution index = Default (0)
    #   Settling, in microseconds = Auto (0)
    aNames = ["AIN0_RESOLUTION_INDEX", "AIN0_SETTLING_US",
              "AIN1_RESOLUTION_INDEX", "AIN1_SETTLING_US"]
    aValues = [0, 0,
               0, 0]
else:
    # LabJack T7 configuration

    # AIN0 and AIN1:
    #   Range = +/-10.0 V (10)
    #   Resolution index = Default (0)
    #   Negative Channel = Single-ended (199)
    #   Settling, in microseconds = Auto (0)
    aNames = ["AIN0_RANGE", "AIN0_RESOLUTION_INDEX",
              "AIN0_NEGATIVE_CH", "AIN0_SETTLING_US",
              "AIN1_RANGE", "AIN1_RESOLUTION_INDEX",
              "AIN1_NEGATIVE_CH", "AIN1_SETTLING_US"]
    aValues = [10, 0,
               199, 0,
               10, 0,
               199, 0]

numFrames = len(aNames)
ljm.eWriteNames(handle, numFrames, aNames, aValues)

print("\nSet configuration:")
for i in range(numFrames):
    print("    %s : %f" % (aNames[i], aValues[i]))

if deviceType == ljm.constants.dtT8:
    # Delay for updated settings to take effect on the T8.
    time.sleep(0.050)

# Read AIN0 and AIN1 from the LabJack with eReadNames in a loop.
numFrames = 2
aNames = ["AIN0", "AIN1"]

print("\nStarting %s read loops.%s\n" % (str(loopAmount), loopMessage))
intervalHandle = 1
ljm.startInterval(intervalHandle, 1000000)  # Delay between readings (in microseconds)
i = 0
while True:
    try:
        results = ljm.eReadNames(handle, numFrames, aNames)
        print("AIN0 : %f V, AIN1 : %f V" % (results[0], results[1]))
        ljm.waitForNextInterval(intervalHandle)
        if loopAmount != "infinite":
            i = i + 1
            if i >= loopAmount:
                break
    except KeyboardInterrupt:
        break
    except Exception:
        print(sys.exc_info()[1])
        break

# Close handles
ljm.cleanInterval(intervalHandle)
ljm.close(handle)
