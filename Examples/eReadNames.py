"""
Demonstrates how to use the labjack.ljm.eReadNames (LJM_eReadNames) function.

"""

from labjack import ljm


# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
#handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Setup and call eReadNames to read values from the LabJack.
numFrames = 3
names = ["SERIAL_NUMBER", "PRODUCT_ID", "FIRMWARE_VERSION"]
results = ljm.eReadNames(handle, numFrames, names)

print("\neReadNames results: ")
for i in range(numFrames):
    print("    Name - %s, value : %f" % (names[i], results[i]))

# Close handle
ljm.close(handle)
