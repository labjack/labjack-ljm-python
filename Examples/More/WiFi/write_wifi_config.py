"""
Demonstrates how to configure the WiFi settings on a LabJack.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    eWriteName:
        https://labjack.com/support/software/api/ljm/function-reference/ljmewritename
    eWriteNames:
        https://labjack.com/support/software/api/ljm/function-reference/ljmewritenames
    IPToNumber:
        https://labjack.com/support/software/api/ljm/function-reference/utility/ljmiptonumber
    NumberToIP:
        https://labjack.com/support/software/api/ljm/function-reference/utility/ljmnumbertoip

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

# Setup and call eWriteNames to configure WiFi default settings on the LabJack.
numFrames = 3
names = ["WIFI_IP_DEFAULT", "WIFI_SUBNET_DEFAULT",
         "WIFI_GATEWAY_DEFAULT"]
aValues = [ljm.ipToNumber("192.168.1.207"), ljm.ipToNumber("255.255.255.0"),
           ljm.ipToNumber("192.168.1.1")]
ljm.eWriteNames(handle, numFrames, names, aValues)

print("\nSet WiFi configuration:")
for i in range(numFrames):
    print("    %s : %.0f - %s" %
          (names[i], aValues[i], ljm.numberToIP(aValues[i])))

# Setup and call eWriteString to configure the default WiFi SSID on the LabJack.
name = "WIFI_SSID_DEFAULT"
string = "LJOpen"
ljm.eWriteNameString(handle, name, string)
print("    %s : %s" % (name, string))

# Setup and call eWriteString to configure the default WiFi password on the
# LabJack.
name = "WIFI_PASSWORD_DEFAULT"
string = "none"
ljm.eWriteNameString(handle, name, string)
print("    %s : %s" % (name, string))

# Setup and call eWriteName to apply the new WiFi configuration on the LabJack.
name = "WIFI_APPLY_SETTINGS"
value = 1
ljm.eWriteName(handle, name, value)
print("    %s : %.0f" % (name, value))

# Close handle
ljm.close(handle)
