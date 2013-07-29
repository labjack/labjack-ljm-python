"""
Demonstrates how to read a single digital input/output.

"""

from labjack import ljm

# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
#handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Setup and call eReadName to read the DIO state from the LabJack.
name = "FIO0"
result = ljm.eReadName(handle, name)

print("\n%s state : %f" % (name, result))

# Close handle
ljm.close(handle)
