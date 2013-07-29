"""
Demonstrates how to use the labjack.ljm.eAddresses (LJM_eAddresses) function.

"""

from labjack import ljm


# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
#handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Setup and call eAddresses to write/read values to/from the LabJack.
numFrames = 3
aAddresses = [1000, 55110, 55110] # [DAC0, TEST_UINT16, TEST_UINT16]
aDataTypes = [ljm.constants.FLOAT32, ljm.constants.UINT16, ljm.constants.UINT16]
aWrites = [ljm.constants.WRITE, ljm.constants.WRITE, ljm.constants.READ]
aNumValues = [1, 1, 1]
aValues = [2.5, 12345, 0] # [write 2.5 V, write 12345, read]
results = ljm.eAddresses(handle, numFrames, aAddresses, aDataTypes, aWrites, aNumValues, aValues)

print("\neAddresses results: ")
start = 0
for i in range(numFrames):
    end = start + aNumValues[i]
    print("    Address - %i, data type - %i, write - %i, values: %s" % \
        (aAddresses[i], aDataTypes[i], aWrites[i], str(results[start:end])))
    start = end

# Close handle
ljm.close(handle)