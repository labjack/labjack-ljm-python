"""
Demonstrates how to use the labjack.ljm.eNames (LJM_eNames) function.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    eNames:
        https://labjack.com/support/software/api/ljm/function-reference/ljmenames

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Hardware Overview(Device Information Registers):
        https://labjack.com/support/datasheets/t-series/hardware-overview

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

# Local constants to save screen space
WRITE = ljm.constants.WRITE
READ = ljm.constants.READ
FLOAT32 = ljm.constants.FLOAT32
UINT16 = ljm.constants.UINT16
UINT32 = ljm.constants.UINT32

# Setup and call eNames to write/read values to/from the LabJack.
# Write 2.5V to DAC0,
# write 12345 to TEST_UINT16,
# read TEST_UINT16,
# read serial number,
# read product ID,
# and read firmware version.
numFrames = 6
aNames = ['DAC0', 'TEST_UINT16', 'TEST_UINT16', 'SERIAL_NUMBER', 'PRODUCT_ID',
          'FIRMWARE_VERSION']
aWrites = [WRITE, WRITE, READ, READ, READ, READ]
aNumValues = [1, 1, 1, 1, 1, 1]
aValues = [2.5, 12345, 0, 0, 0, 0]
results = ljm.eNames(handle, numFrames, aNames, aWrites, aNumValues, aValues)

print("\neNames results: ")
start = 0
for i in range(numFrames):
    end = start + aNumValues[i]
    print("    Name - %16s, write - %i, values %s" %
          (aNames[i], aWrites[i], results[start:end]))
    start = end

# Close handle
ljm.close(handle)
