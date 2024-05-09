"""
Demonstrates ReadLibraryConfigS and ReadLibraryConfigStringS.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Constants:
        https://labjack.com/support/software/api/ljm/constants
    Library Configuration Functions:
        https://labjack.com/support/software/api/ljm/function-reference/library-configuration-functions

"""
from labjack import ljm

# Read the name of the error constants file being used by LJM
configString = "LJM_ERROR_CONSTANTS_FILE"
print("%s: %s" % (configString, ljm.readLibraryConfigStringS(configString)))

# Write the communication send/receive timeout for LJM
configString = "LJM_SEND_RECEIVE_TIMEOUT_MS"
ljm.writeLibraryConfigS(configString, 5000)

# Read the communication send/receive timeout for LJM
print("%s: %d" % (configString, ljm.readLibraryConfigS(configString)))
