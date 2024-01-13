"""
Demonstrates configuring and reading a single analog input (AIN) with a LabJack.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    eReadName:
        https://labjack.com/support/software/api/ljm/function-reference/ljmereadname
    Multiple Value Functions(such as eWriteNames):
        https://labjack.com/support/software/api/ljm/function-reference/multiple-value-functions

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
from time import sleep

from labjack import ljm


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

# Setup and call eWriteNames to configure AIN0 on the LabJack.
if deviceType == ljm.constants.dtT8:
    # LabJack T8 configuration

    # AIN0:
    #   Range = +/-11.0 V (11)
    # AIN all resolution index = Default (0)
    # AIN sampling rate, in Hz = Auto (0)
    aNames = ["AIN0_RANGE", "AIN_ALL_RESOLUTION_INDEX", "AIN_SAMPLING_RATE_HZ"]
    aValues = [11, 0, 0]
elif deviceType == ljm.constants.dtT4:
    # LabJack T4 configuration

    # AIN0:
    #   Resolution index = Default (0)
    #   Settling, in microseconds = Auto (0)
    aNames = ["AIN0_RESOLUTION_INDEX", "AIN0_SETTLING_US"]
    aValues = [0, 0]
else:
    # LabJack T7 configuration

    # AIN0:
    #   Range = +/-10.0 V (10)
    #   Resolution index = Default (0)
    #   Negative Channel = Single-ended (199)
    #   Settling, in microseconds = Auto (0)
    aNames = ["AIN0_RANGE", "AIN0_RESOLUTION_INDEX", "AIN0_NEGATIVE_CH",
              "AIN0_SETTLING_US"]
    aValues = [10, 0, 199,
               0]

numFrames = len(aNames)
ljm.eWriteNames(handle, numFrames, aNames, aValues)

print("\nSet configuration:")
for i in range(numFrames):
    print("    %s : %f" % (aNames[i], aValues[i]))

if deviceType == ljm.constants.dtT8:
    # Delay for updated settings to take effect on the T8.
    sleep(0.050)

# Setup and call eReadName to read AIN0 from the LabJack.
name = "AIN0"
result = ljm.eReadName(handle, name)

print("\n%s reading : %f V" % (name, result))

# Close handle
ljm.close(handle)
