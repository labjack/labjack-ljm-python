"""
Demonstrates how to use the labjack.ljm.eReadAddress (LJM_eReadAddress)
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

# Setup and call eReadAddress to read a value from the LabJack.
address = 60028  # Serial number
dataType = ljm.constants.UINT32
result = ljm.eReadAddress(handle, address, dataType)

print("\neReadAddress result: ")
print("    Address - %i, data type - %i, value : %f" %
      (address, dataType, result))

# Close handle
ljm.close(handle)
