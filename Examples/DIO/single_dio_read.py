"""
Demonstrates how to read a single digital input/output.

"""
from labjack import ljm


# Open first found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
#handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
#handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
#handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

deviceType = info[0]

# Setup and call eReadName to read a DIO state from the LabJack.
if deviceType == ljm.constants.dtT4:
    # Reading from FIO4 on the LabJack T4. FIO0-FIO3 are reserved for AIN0-AIN3.
    # Note: Reading a single digital I/O will change the line from analog to
    # digital input.
    name = "FIO4"
else:
    # Reading from FIO0 on the LabJack T7 and other devices.
    name = "FIO0"
result = ljm.eReadName(handle, name)

print("\n%s state : %f" % (name, result))

# Close handle
ljm.close(handle)
