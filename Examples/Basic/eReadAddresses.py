"""
Demonstrates how to use the labjack.ljm.eReadAddresses (LJM_eReadAddresses)
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

# Setup and call eReadAddresses to read values from the LabJack.
numFrames = 3
aAddresses = [60028, 60000, 60004]  # [serial number, product ID, firmware version]
aDataTypes = [ljm.constants.UINT32, ljm.constants.FLOAT32,
              ljm.constants.FLOAT32]
results = ljm.eReadAddresses(handle, numFrames, aAddresses, aDataTypes)

print("\neReadAddresses results: ")
for i in range(numFrames):
    print("    Address - %i, data type - %i, value : %f" %
          (aAddresses[i], aDataTypes[i], results[i]))

# Close handle
ljm.close(handle)
