"""
Demonstrates configuring and reading a single analog input (AIN) with a LabJack.

"""

from labjack import ljm

# Open first found LabJack
handle = ljm.openS("T4", "ANY", "ANY")
#handle = ljm.open(ljm.constants.dtT4, ljm.constants.ctANY, "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Setup and call eWriteNames to configure the AIN on the LabJack.
numFrames = 3
names = ["AIN4_NEGATIVE_CH", "AIN4_RANGE", "AIN4_RESOLUTION_INDEX"] #["AIN0_NEGATIVE_CH", "AIN0_RANGE", "AIN0_RESOLUTION_INDEX"]
aValues = [199, 3.3, 0]
ljm.eWriteNames(handle, numFrames, names, aValues)

print("\nSet configuration:")
for i in range(numFrames):
    print("    %s : %f" % (names[i], aValues[i]))

# Setup and call eReadName to read an AIN from the LabJack.
name = "AIN4" # "AIN0"
result = ljm.eReadName(handle, name)

print("\n%s reading : %f V" % (name, result))

# Close handle
ljm.close(handle)
