"""
Demonstrates how to use the labjack.ljm.eWriteAddresses (LJM_eWriteAddresses)
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

# Setup and call eWriteAddresses to write values to the LabJack.
numFrames = 2
aAddresses = [1000, 55110]  # [DAC0, TEST_UINT16]
aDataTypes = [ljm.constants.FLOAT32, ljm.constants.UINT16]
aValues = [2.5, 12345]  # [write 2.5 V, write 12345]
ljm.eWriteAddresses(handle, numFrames, aAddresses, aDataTypes, aValues)

print("\neWriteAddresses: ")
for i in range(numFrames):
    print("    Address - %i, data type - %i, value : %f" %
          (aAddresses[i], aDataTypes[i], aValues[i]))

# Close handle
ljm.close(handle)
