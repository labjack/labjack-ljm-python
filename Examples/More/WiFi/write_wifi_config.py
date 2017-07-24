"""
Demonstrates how to configure the WiFi settings on a LabJack.

"""
import sys

from labjack import ljm


# Open first found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
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
