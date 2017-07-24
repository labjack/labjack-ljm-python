"""
Demonstrates usage of the listAll functions (LJM_ListAll) which scans for
LabJack devices and returns information describing the found devices. This will
only find LabJack devices supported by the LJM library.

"""
from labjack import ljm


DEVICE_TYPES = {ljm.constants.dtT7: "T7",
                ljm.constants.dtT4: "T4",
                ljm.constants.dtDIGIT: "Digit"}
CONN_TYPES = {ljm.constants.ctUSB: "USB",
              ljm.constants.ctTCP: "TCP",
              ljm.constants.ctETHERNET: "Ethernet",
              ljm.constants.ctWIFI: "WiFi"}


def displayDeviceInfo(functionName, info):
    """Displays the LabJack devices information from listAll or
    listAllS.

    Args:
       functionName: The name of the function used
       info: tuple returned by listAll or listAllS

    """
    print("\n%s found %i LabJacks:\n" % (functionName, info[0]))
    fmt = ''.join(["{%i:<18}" % i for i in range(0, 4)])
    print(fmt.format("Device Type", "Connection Type", "Serial Number",
                     "IP Address"))
    for i in range(info[0]):
        print(fmt.format(DEVICE_TYPES.setdefault(info[1][i], str(info[1][i])),
                         CONN_TYPES.setdefault(info[2][i], str(info[2][i])),
                         str(info[3][i]), ljm.numberToIP(info[4][i])))


# listAll and listAllS returns the tuple (numFound, aDeviceTypes,
# aConnectionTypes, aSerialNumbers, aIPAddresses)

# Find and display LabJack devices with listAllS.
info = ljm.listAllS("ANY", "ANY")
displayDeviceInfo("listAllS", info)

"""
# Find and display LabJack devices with listAll.
info = ljm.listAll(ljm.constants.ctANY, ljm.constants.ctANY)
displayDeviceInfo("listAll", info)
"""
