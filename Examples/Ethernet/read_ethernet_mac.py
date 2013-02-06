"""
Demonstrates how to read the ethernet MAC from a LabJack.

"""

from labjack import ljm
import struct

# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "LJM_idANY")[2]
#handle = ljm.openS("LJM_dtANY", "LJM_ctANY", "LJM_idANY")

info = ljm.getHandleInfo(handle)
print "Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5])

# Call eAddresses to read the ethernet MAC from the LabJack. Note that we are
# reading a byte array which is the big endian binary representation of the
# 64-bit MAC.
macBytes = ljm.eAddresses(handle, 1, [60020], [ljm.constants.BYTE],
                          [ljm.constants.READ], [8], [0]*8)
# Convert big endian byte array to a 64-bit unsigned integer value
mac, = struct.unpack(">Q", struct.pack("B"*8, *macBytes))

print "\nMAC : %s  (%i)" % (ljm.numberToMAC(mac), mac)

# Close handle
ljm.close(handle)
