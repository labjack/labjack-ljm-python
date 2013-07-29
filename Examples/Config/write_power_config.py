"""
Demonstrates how to configure default power settings on a LabJack.

"""

from labjack import ljm


# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
#handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Setup and call eWriteNames to write config. values to the LabJack.
numFrames = 4
names = ["POWER_ETHERNET_DEFAULT", "POWER_WIFI_DEFAULT", "POWER_AIN_DEFAULT",
         "POWER_LED_DEFAULT"]
aValues = [1, 0, 1,
           1]
ljm.eWriteNames(handle, numFrames, names, aValues)

print("\nSet configuration settings:")

for i in range(numFrames):
    print("    %s : %f" % (names[i], aValues[i]))

# Close handle
ljm.close(handle)
