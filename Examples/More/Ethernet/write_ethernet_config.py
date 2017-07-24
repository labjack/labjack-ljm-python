"""
Demonstrates how to set ethernet configuration settings on a LabJack.

"""
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

# Setup and call eWriteNames to set the ethernet configuration on the LabJack.
numFrames = 4
names = ["ETHERNET_IP_DEFAULT", "ETHERNET_SUBNET_DEFAULT",
         "ETHERNET_GATEWAY_DEFAULT", "ETHERNET_DHCP_ENABLE_DEFAULT"]
values = [ljm.ipToNumber("192.168.1.207"), ljm.ipToNumber("255.255.255.0"),
          ljm.ipToNumber("192.168.1.1"), 1]
ljm.eWriteNames(handle, numFrames, names, values)

print("\nSet ethernet configuration:")
for i in range(numFrames):
    if names[i] == "ETHERNET_DHCP_ENABLE_DEFAULT":
        print("    %s : %.0f" % (names[i], values[i]))
    else:
        print("    %s : %.0f - %s" %
              (names[i], values[i], ljm.numberToIP(int(values[i]))))

# Close handle
ljm.close(handle)
