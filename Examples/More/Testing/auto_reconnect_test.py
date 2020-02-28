"""
Tests the LJM auto reconnect functionality.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    WriteLibraryConfigS:
        https://labjack.com/support/software/api/ljm/function-reference/LJMWriteLibraryConfigS
    RegisterDeviceReconnectCallback:
        https://labjack.com/support/software/api/ljm/function-reference/LJMRegisterDeviceReconnectCallback
    eReadName:
        https://labjack.com/support/software/api/ljm/function-reference/ljmereadname

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Hardware Overview (Device Information Registers):
        https://labjack.com/support/datasheets/t-series/hardware-overview

"""
import sys
import threading
import time

from labjack import ljm


try:
    input = raw_input  # Set input to raw_input for Python 2.x
except:
    pass

def myReconnectCallback(handle):
    print("Reconnected handle: %s" % handle)


# Set the timeouts shorter for testing convenience
ljm.writeLibraryConfigS(ljm.constants.OPEN_TCP_DEVICE_TIMEOUT_MS, 500)
ljm.writeLibraryConfigS(ljm.constants.SEND_RECEIVE_TIMEOUT_MS, 500)

# Open first found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
#handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
#handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
#handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

ljm.registerDeviceReconnectCallback(handle, myReconnectCallback)

print("\nPress Ctrl+C to exit.")
i = 0
while True:
    try:
        try:
            i = i + 1
            print("\nIteration: %d" % i)

            # Read the serial number from the device
            name = "SERIAL_NUMBER"
            value = ljm.eReadName(handle, name)
            print("  Read %s: %.0f" % (name, value))

            # Above read succeeded. Displaying device information.
            info = ljm.getHandleInfo(handle)
            print("  Handle: %i, Device type: %i, Connection type: %i, Serial number: %i,\n"
                  "  IP address: %s, Port: %i, Max bytes per MB: %i" %
                  (handle, info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            print("  " + str(ljme))

        print("  Unplug, replug, wait")
        input("  Press Enter to continue\n")
    except KeyboardInterrupt:
        break
    except:
        print(sys.exc_info()[1])
        break

# Close handle
ljm.close(handle)
