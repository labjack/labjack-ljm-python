"""
Demonstrates how to set a single digital state on a LabJack.

"""

from labjack import ljm

# Open first found LabJack
handle = ljm.openS("T4", "ANY", "ANY")
#handle = ljm.open(ljm.constants.dtT4, ljm.constants.ctANY, "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

ljm.eWriteAddress(handle, 2875, ljm.constants.UINT32, 0)  # remove


# Setup and call eWriteName to set the DIO state on the LabJack.
name = "FIO7"
state = 0
#ljm.eWriteName(handle, name, state)

print("\nSet %s state : %f" % (name, state))
'''
state = 0
for i in range(20):
    if i % 2:
        state += 1 << i
print(state)
'''
ljm.eWriteName(handle, "DIO_DIRECTION", 0x0FFFFF) #1048575)
#ljm.eWriteName(handle, "DIO_STATE", 0x0FF0F0)
ljm.eWriteName(handle, "FIO0", 1)

#ljm.eWriteName(handle, "CIO_STATE", 0x03)

val = ljm.eReadName(handle, "MIO0")
print(val)

# Close handle
ljm.close(handle)
