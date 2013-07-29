"""
Demonstrates how to set a single digital state on a LabJack.

"""

from labjack import ljm

# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
#handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Setup and call eWriteName to set the DIO state on the LabJack.
name = "FIO0"
state = 0
ljm.eWriteName(handle, name, state)

print("\nSet %s state : %f" % (name, state))

# Close handle
ljm.close(handle)
