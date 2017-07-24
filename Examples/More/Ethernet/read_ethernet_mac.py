"""
Demonstrates how to read the ethernet MAC from a LabJack.

"""
import struct

from labjack import ljm


# Open first found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
#handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
#handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
#handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Call eReadAddressByteArray to read the ethernet MAC (address 60020) from the
# LabJack. We are reading a byte array which is the big endian binary
# representation of the 64-bit MAC.
macBytes = ljm.eReadAddressByteArray(handle, 60020, 8)

# Convert big endian byte array to a 64-bit unsigned integer value
mac, = struct.unpack(">Q", struct.pack("B"*8, *macBytes))

print("\nEthernet MAC : %i - %s" % (mac, ljm.numberToMAC(mac)))

# Close handle
ljm.close(handle)
