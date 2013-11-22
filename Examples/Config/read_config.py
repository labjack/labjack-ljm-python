"""
Demonstrates how to read configuration settings on a LabJack.

"""

from labjack import ljm


# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
#handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Setup and call eReadNames to read config. values from the LabJack.
names = ["PRODUCT_ID", "HARDWARE_VERSION", "FIRMWARE_VERSION",
         "BOOTLOADER_VERSION", "WIFI_VERSION", "SERIAL_NUMBER",
         "POWER_ETHERNET_DEFAULT", "POWER_WIFI_DEFAULT", "POWER_AIN_DEFAULT",
         "POWER_LED_DEFAULT"]
numFrames = len(names)
results = ljm.eReadNames(handle, numFrames, names)

print("\nConfiguration settings:")
for i in range(numFrames):
    print("    %s : %f" % (names[i], results[i]))

# Close handle
ljm.close(handle)
