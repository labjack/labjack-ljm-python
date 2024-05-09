"""
Demonstrates how to read the WiFi MAC from a LabJack.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    eReadAddressByteArray:
        https://labjack.com/support/software/api/ljm/function-reference/ljmereadaddressbytearray
    NumberToMAC:
        https://labjack.com/support/software/api/ljm/function-reference/utility/ljmnumbertomac

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    WiFi:
        https://labjack.com/support/datasheets/t-series/wifi

Note:
    Our Python interfaces throw exceptions when there are any issues with
    device communications that need addressed. Many of our examples will
    terminate immediately when an exception is thrown. The onus is on the API
    user to address the cause of any exceptions thrown, and add exception
    handling when appropriate. We create our own exception classes that are
    derived from the built-in Python Exception class and can be caught as such.
    For more information, see the implementation in our source code and the
    Python standard documentation.
"""
import struct
import sys

from labjack import ljm


# Open first found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
#handle = ljm.openS("T8", "ANY", "ANY")  # T8 device, Any connection, Any identifier
#handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
#handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

if info[0] == ljm.constants.dtT4:
    print("\nThe LabJack T4 does not support WiFi.")
    sys.exit()

# Call eReadAddressByteArray to read the WiFi MAC (address 60024) from the
# LabJack. We are reading a byte array which is the big endian binary
# representation of the 64-bit MAC.
macBytes = ljm.eReadAddressByteArray(handle, 60024, 8)

# Convert big endian byte array to a 64-bit unsigned integer value
mac, = struct.unpack(">Q", struct.pack("B"*8, *macBytes))

print("\nWiFi MAC : %i - %s" % (mac, ljm.numberToMAC(mac)))

# Close handle
ljm.close(handle)
