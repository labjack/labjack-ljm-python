"""
Demonstrates reading a single analog input (AIN) from a LabJack T4.

"""

from labjack import ljm

# Open first found LabJack
handle = ljm.openS("T4", "USB", "ANY")
# handle = ljm.open(ljm.constants.dtT4, ljm.constants.ctANY, "ANY")

info = ljm.getHandleInfo(handle)
print(info[4])
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Setup and call eReadName to read from a AIN on the LabJack.
name = "AIN0"
result = ljm.eReadName(handle, name)

print("\n%s reading : %f V" % (name, result))

# Close handle
ljm.close(handle)
