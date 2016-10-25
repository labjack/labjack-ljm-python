"""
Demonstrates how to read the WiFi configuration from a LabJack.

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

# Setup and call eReadNames to read WiFi configuration from the LabJack.
names = ["WIFI_IP", "WIFI_SUBNET", "WIFI_GATEWAY", "WIFI_DHCP_ENABLE",
         "WIFI_IP_DEFAULT", "WIFI_SUBNET_DEFAULT", "WIFI_GATEWAY_DEFAULT",
         "WIFI_DHCP_ENABLE_DEFAULT", "WIFI_STATUS"]
numFrames = len(names)
results = ljm.eReadNames(handle, numFrames, names)
print("\nWiFi configuration: ")
for i in range(numFrames):
    if names[i] == "WIFI_STATUS" or names[i].startswith("WIFI_DHCP_ENABLE"):
        print("    %s : %.0f" % (names[i], results[i]))
    else:
        print("    %s : %.0f - %s" %
              (names[i], results[i], ljm.numberToIP(int(results[i]))))

# Setup and call eReadNameString to read the WiFi SSID string from the LabJack.
name = "WIFI_SSID"
result = ljm.eReadNameString(handle, name)
print("    %s : %s" % (name, result))

# Close handle
ljm.close(handle)
