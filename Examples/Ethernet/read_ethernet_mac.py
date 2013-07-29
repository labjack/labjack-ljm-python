"""
Demonstrates how to read the ethernet MAC from a LabJack.

"""

from labjack import ljm
import struct

# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
#handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Call eAddresses to read the ethernet MAC from the LabJack. Note that we are
# reading a byte array which is the big endian binary representation of the
# 64-bit MAC.
macBytes = ljm.eAddresses(handle, 1, [60020], [ljm.constants.BYTE],
                          [ljm.constants.READ], [8], [0]*8)
# Convert returned values to integers
macBytes = [int(b) for b in macBytes]
# Convert big endian byte array to a 64-bit unsigned integer value
mac, = struct.unpack(">Q", struct.pack("B"*8, *macBytes))

print("\nEthernet MAC : %i - %s" % (mac, ljm.numberToMAC(mac)))

# Close handle
ljm.close(handle)
