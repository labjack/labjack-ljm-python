"""
Demonstrates configuring and reading a single analog input (AIN).

"""

from labjack import ljm

# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "LJM_idANY")[2]
#handle = ljm.openS("LJM_dtANY", "LJM_ctANY", "LJM_idANY")

info = ljm.getHandleInfo(handle)
print "Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5])

# Setup and call eWriteNames to configure the AIN on the LabJack.
numFrames = 4
names = ["AIN0_NEGATIVE", "AIN0_RANGE", "AIN0_RESOLUTION", "AIN0_SETTLING"]
aValues = [199, 10, 0, 0]
ljm.eWriteNames(handle, numFrames, names, aValues)

# Setup and call eReadName to read an AIN from the LabJack.
name = "AIN0"
result = ljm.eReadName(handle, name)

print "\nResult: "
print "    %s value: %f V" % (name, result)

# Close handle
ljm.close(handle)
