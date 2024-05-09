"""
Demonstrates ReadLibraryConfigS, ReadLibraryConfigStringS and
WriteLibraryConfigS usage.

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

Note:
    Our Python interfaces throw exceptions when there are any issues with
    device communications that need addressed. Many of our examples will
    terminate immediately when an exception is thrown. The onus is on the API
    user to address the cause of any exceptions thrown, and add exception
    handling when appropriate. We create our own exception classes that are
    derived from the built-in Python Exception class and can be caught as such.
    For more information, see the implementation in our source code and the
    Python standard documentation.
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
