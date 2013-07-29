"""
Demonstrates how to use the labjack.ljm.eNames (LJM_eNames) function.

"""

from labjack import ljm


# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
#handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Setup and call eNames to write/read values to/from the LabJack.
numFrames = 3
names = ["DAC0", "TEST_UINT16", "TEST_UINT16"]
aWrites = [ljm.constants.WRITE, ljm.constants.WRITE, ljm.constants.READ]
aNumValues = [1, 1, 1]
aValues = [2.5, 12345, 0] # [write 2.5 V, write 12345, read]
results = ljm.eNames(handle, numFrames, names, aWrites, aNumValues, aValues)

print("\neNames results: ")
start = 0
for i in range(numFrames):
    end = start + aNumValues[i]
    print("    Name - %s, write - %i, values %s" % \
        (names[i], aWrites[i], results[start:end]))
    start = end

# Close handle
ljm.close(handle)