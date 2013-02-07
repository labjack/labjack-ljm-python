"""
Demonstrates how to read the Wifi configuration from a LabJack.

"""

from labjack import ljm

# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "LJM_idANY")[2]
#handle = ljm.openS("LJM_dtANY", "LJM_ctANY", "LJM_idANY")

info = ljm.getHandleInfo(handle)
print "Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5])

# Setup and call eReadNames to read WiFi configuration from the LabJack.
numFrames = 4
names = ["WIFI_IP", "WIFI_SUBNET", "WIFI_GATEWAY", "WIFI_STATUS"]
results = ljm.eReadNames(handle, numFrames, names)

print "\neWifi configuration: "
for i in range(numFrames):
    if names[i] == "WIFI_STATUS":
        print "    %s : %.0f" % (names[i], results[i])
    else:
        print "    %s : %.0f - %s" % \
            (names[i], results[i], ljm.numberToIP(int(results[i])))

# Setup and call eReadString to read the WiFi SSID string from the LabJack.
name = "WIFI_SSID"
result = ljm.eReadString(handle, name)

print "    %s : %s" % (name, result)

# Close handle
ljm.close(handle)
