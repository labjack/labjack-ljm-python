"""
Demonstrates how to set a single digital state on a LabJack.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    eWriteName:
        https://labjack.com/support/software/api/ljm/function-reference/ljmewritename

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Digital I/O:
        https://labjack.com/support/datasheets/t-series/digital-io

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
#handle = ljm.openS("T8", "ANY", "ANY")  # T8 device, Any connection, Any identifier
#handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
#handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
#handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

deviceType = info[0]

# Setup and call eWriteName to set a DIO state on the LabJack.
if deviceType == ljm.constants.dtT4:
    # Setting FIO4 on the LabJack T4. FIO0-FIO3 are reserved for AIN0-AIN3.
    name = "FIO4"

    # If the FIO/EIO line is an analog input, it needs to first be changed to a
    # digital I/O by reading from the line or setting it to digital I/O with the
    # DIO_ANALOG_ENABLE register.

    # Reading from the digital line in case it was previously an analog input.
    ljm.eReadName(handle, name)
else:
    # Setting FIO0 on the LabJack T7 and T8.
    name = "FIO0"

state = 0  # Output state = low (0 = low, 1 = high)
ljm.eWriteName(handle, name, state)
print("\nSet %s state : %f" % (name, state))

# Close handle
ljm.close(handle)
