"""
Demonstrates how to read the Watchdog configuration from a LabJack.

"""

from labjack import ljm


# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "LJM_idANY")[0]
#handle = ljm.openS("LJM_dtANY", "LJM_ctANY", "LJM_idANY")

info = ljm.getHandleInfo(handle)
print "Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5])

# Setup and call eReadNames to read the Watchdog config. from the LabJack.
names = ["WATCHDOG_ENABLE_DEFAULT", "WATCHDOG_OPTIONS_DEFAULT",
         "WATCHDOG_TIMEOUT_S_DEFAULT", "WATCHDOG_STARTUP_DELAY_S_DEFAULT",
         "WATCHDOG_DIO_STATE_DEFAULT", "WATCHDOG_DIO_DIRECTION_DEFAULT",
         "WATCHDOG_DIO_MASK_DEFAULT", "WATCHDOG_DAC0_DEFAULT",
         "WATCHDOG_DAC1_DEFAULT"]
numFrames = len(names)
results = ljm.eReadNames(handle, numFrames, names)

print "\nWatchdog configuration:"
for i in range(numFrames):
    print "    %s : %f" % (names[i], results[i])

# Close handle
ljm.close(handle)
