"""
Simple asynch example using the first found device and 9600/8/N/1.
Does a write, waits 1 second, then returns whatever was read in that
time. If you short RX to TX, then you will read back the same bytes that you
write.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    eWriteName:
        https://labjack.com/support/software/api/ljm/function-reference/ljmewritename
    Multiple Value Functions(such as eWriteNameByteArray):
        https://labjack.com/support/software/api/ljm/function-reference/multiple-value-functions

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Digital I/O:
        https://labjack.com/support/datasheets/t-series/digital-io
    Asynchronous Serial:
        https://labjack.com/support/datasheets/t-series/digital-io/asynchronous-serial

"""
from time import sleep

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

deviceType = info[0]

# Configure the asynch feature
ljm.eWriteName(handle, "ASYNCH_ENABLE", 0)
if deviceType == ljm.constants.dtT4:
    # Configure FIO4, FIO5, and FIO6 as digital I/O.
    ljm.eWriteName(handle, "DIO_INHIBIT", 0xFFF8F)
    ljm.eWriteName(handle, "DIO_ANALOG_ENABLE", 0x00000)

    # For the T4, using FIO4 and FIO5 for RX and TX pins. FIO0 to FIO3 are
    # reserved for analog inputs, and digital lines are required.
    ljm.eWriteName(handle, "ASYNCH_RX_DIONUM", 4)  # RX pin number = 4 (FIO4)
    ljm.eWriteName(handle, "ASYNCH_TX_DIONUM", 5)  # TX pin number = 5 (FIO5)
else:
    # For the T7 and T8, use FIO0 and FIO1 for the RX and TX pins.
    ljm.eWriteName(handle, "ASYNCH_RX_DIONUM", 0)  # RX pin number = 0 (FIO0)
    ljm.eWriteName(handle, "ASYNCH_TX_DIONUM", 1)  # TX pin number = 1 (FIO1)

ljm.eWriteName(handle, "ASYNCH_BAUD", 9600)
ljm.eWriteName(handle, "ASYNCH_NUM_DATA_BITS", 8)
ljm.eWriteName(handle, "ASYNCH_PARITY", 0)
ljm.eWriteName(handle, "ASYNCH_NUM_STOP_BITS", 1)
ljm.eWriteName(handle, "ASYNCH_ENABLE", 1)

writeValues = [0x12, 0x34, 0x56, 0x78]
numBytes = len(writeValues)
print("Writing:")
print([hex(x) for x in writeValues])
ljm.eWriteName(handle, "ASYNCH_NUM_BYTES_TX", numBytes)
ljm.eWriteNameArray(handle, "ASYNCH_DATA_TX", numBytes, writeValues)
ljm.eWriteName(handle, "ASYNCH_TX_GO", 1)

sleep(1)

readValues = ljm.eReadNameArray(handle, "ASYNCH_DATA_RX", numBytes)
print("\nRead:")
print([hex(int(val)) for val in readValues])

# Close handle
ljm.close(handle)
