"""
Demonstrates how to configure the the Watchdog on a LabJack.

"""

from labjack import ljm


# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "LJM_idANY")[2]
#handle = ljm.openS("LJM_dtANY", "LJM_ctANY", "LJM_idANY")

info = ljm.getHandleInfo(handle)
print "Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5])

# Setup and call eWriteNames to configure the Watchdog on a LabJack.
# Disable the Watchdog first before any other configuration.
numFrames = 11
names = ["WATCHDOG_ENABLE_DEFAULT", "WATCHDOG_OPTIONS_DEFAULT",
         "WATCHDOG_TIMEOUT_DEFAULT", "WATCHDOG_STARTUP_DELAY_DEFAULT",
         "WATCHDOG_DIO_STATE_DEFAULT", "WATCHDOG_DIO_DIRECTION_DEFAULT",
         "WATCHDOG_DIO_MASK_DEFAULT", "WATCHDOG_DAC0_DEFAULT",
         "WATCHDOG_DAC1_DEFAULT", "WATCHDOG_KEY_DEFAULT",
         "WATCHDOG_ENABLE_DEFAULT"]
values = [0, 1,
          20, 0,
          0, 0,
          0, 0,
          0, 0,
          0] # Set 10th element to 1 to enable
ljm.eWriteNames(handle, numFrames, names, values)

print "\nSet Watchdog configuration:"
for i in range(numFrames):
    print "    %s : %f" % (names[i], values[i])

# Close handle
ljm.close(handle)
