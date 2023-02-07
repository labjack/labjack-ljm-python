"""
Demonstrates how to configure the Watchdog on a LabJack.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    eWriteNames:
        https://labjack.com/support/software/api/ljm/function-reference/ljmewritenames

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Watchdog:
        https://labjack.com/support/datasheets/t-series/watchdog

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

# Setup and call eWriteNames to configure the Watchdog on a LabJack.
# Disable the Watchdog first before any other configuration.
aNames = ["WATCHDOG_ENABLE_DEFAULT", "WATCHDOG_ADVANCED_DEFAULT",
          "WATCHDOG_TIMEOUT_S_DEFAULT", "WATCHDOG_STARTUP_DELAY_S_DEFAULT",
          "WATCHDOG_STRICT_ENABLE_DEFAULT", "WATCHDOG_STRICT_KEY_DEFAULT",
          "WATCHDOG_RESET_ENABLE_DEFAULT", "WATCHDOG_DIO_ENABLE_DEFAULT",
          "WATCHDOG_DIO_STATE_DEFAULT", "WATCHDOG_DIO_DIRECTION_DEFAULT",
          "WATCHDOG_DIO_INHIBIT_DEFAULT", "WATCHDOG_DAC0_ENABLE_DEFAULT",
          "WATCHDOG_DAC0_DEFAULT", "WATCHDOG_DAC1_ENABLE_DEFAULT",
          "WATCHDOG_DAC1_DEFAULT", "WATCHDOG_ENABLE_DEFAULT"]
aValues = [0, 0,
           20, 0,  # Timeout set to 20 seconds
           0, 0,
           1, 0,  # Reset the device on timeout
           0, 0,
           0, 0,
           0, 0,
           0, 0]  # Set the last WATCHDOG_ENABLE_DEFAULT to 1 to enable
numFrames = len(aNames)
ljm.eWriteNames(handle, numFrames, aNames, aValues)

print("\nSet Watchdog configuration:")
for i in range(numFrames):
    print("    %s : %f" % (aNames[i], aValues[i]))

# Close handle
ljm.close(handle)
