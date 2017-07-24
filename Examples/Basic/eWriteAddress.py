"""
Demonstrates how to use the labjack.ljm.eWriteAddress (LJM_eWriteAddress)
function.

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

# Setup and call eWriteAddress to write a value to the LabJack.
address = 1000  # DAC0
dataType = ljm.constants.FLOAT32
value = 2.5  # 2.5 V
ljm.eWriteAddress(handle, address, dataType, value)

print("\neWriteAddress: ")
print("    Address - %i, data type - %i, value : %f" %
      (address, dataType, value))

# Close handle
ljm.close(handle)
