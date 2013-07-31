"""
Demonstrates how to read the device name string from a LabJack.

"""

from labjack import ljm


# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
#handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Call eReadNameString to read the name string from the LabJack.
string = ljm.eReadNameString(handle, "DEVICE_NAME_DEFAULT")

print("\nDevice name : %s" % string)

# Close handle
ljm.close(handle)
