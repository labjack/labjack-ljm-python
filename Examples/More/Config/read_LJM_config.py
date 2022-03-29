"""
Demonstrates ReadLibraryConfigS and ReadLibraryConfigStringS

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Constants:
        https://labjack.com/support/software/api/ljm/constants
    Library configuration functions:
        https://labjack.com/support/software/api/ljm/function-reference/library-configuration-functions

"""
from labjack import ljm


# Open first found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
#handle = ljm.openS("T8", "ANY", "ANY")  # T8 device, Any connection, Any identifier
#handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
#handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
#handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Read the name of the error constants file being used by LJM
configString = "LJM_ERROR_CONSTANTS_FILE"
print("%s: %s" % (configString, ljm.readLibraryConfigStringS(configString)))

# Read the communication send/receive timeout being used by LJM
configString = "LJM_SEND_RECEIVE_TIMEOUT_MS"
print("%s: %d" % (configString, ljm.readLibraryConfigS(configString)))

# Close handle
ljm.close(handle)
