"""
Demonstrates I2C communication using a LabJack. The demonstration uses a
LJTick-DAC connected to FIO0/FIO1 for the T7 or FIO4/FIO5 for the T4, and
configures the I2C settings. Then a read, write and again a read are performed
on the LJTick-DAC EEPROM.

"""
from random import randrange

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

# Configure the I2C communication.
if deviceType == ljm.constants.dtT4:
    # Configure FIO4 and FIO5 as digital I/O.
    ljm.eWriteName(handle, "DIO_INHIBIT", 0xFFFCF)
    ljm.eWriteName(handle, "DIO_ANALOG_ENABLE", 0x00000)

    # For the T4, using FIO4 and FIO5 for SCL and SDA pins. FIO0 to FIO3 are
    # reserved for analog inputs, and digital lines are required.
    ljm.eWriteName(handle, "I2C_SDA_DIONUM", 5)  # SDA pin number = 5 (FIO5)
    ljm.eWriteName(handle, "I2C_SCL_DIONUM", 4)  # SCL pin number = 4 (FIO4)
else:
    # For the T7 and other devices, using FIO0 and FIO1 for the SCL and SDA
    # pins.
    ljm.eWriteName(handle, "I2C_SDA_DIONUM", 1)  # SDA pin number = 1 (FIO1)
    ljm.eWriteName(handle, "I2C_SCL_DIONUM", 0)  # SCL pin number = 0 (FIO0)

# Speed throttle is inversely proportional to clock frequency. 0 = max.
ljm.eWriteName(handle, "I2C_SPEED_THROTTLE", 65516)  # Speed throttle = 65516 (~100 kHz)

# Options bits:
#     bit0: Reset the I2C bus.
#     bit1: Restart w/o stop
#     bit2: Disable clock stretching.
ljm.eWriteName(handle, "I2C_OPTIONS", 0)  # Options = 0

ljm.eWriteName(handle, "I2C_SLAVE_ADDRESS", 80)  # Slave Address of the I2C chip = 80 (0x50)

# Initial read of EEPROM bytes 0-3 in the user memory area. We need a single I2C
# transmission that writes the chip's memory pointer and then reads the data.
ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 1)  # Set the number of bytes to transmit
ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 4)  # Set the number of bytes to receive

# Set the TX bytes. We are sending 1 byte for the address.
numBytes = 1
aBytes = [0]  # Byte 0: Memory pointer = 0
ljm.eWriteNameByteArray(handle, "I2C_DATA_TX", numBytes, aBytes)

ljm.eWriteName(handle, "I2C_GO", 1)  # Do the I2C communications.

# Read the RX bytes.
numBytes = 4
# aBytes[0] to aBytes[3] will contain the data
aBytes = [0]*4
aBytes = ljm.eReadNameByteArray(handle, "I2C_DATA_RX", numBytes)

print("\nRead User Memory [0-3] = %s" %
      " ".join([("%.0f" % val) for val in aBytes]))

# Write EEPROM bytes 0-3 in the user memory area, using the page write
# technique.  Note that page writes are limited to 16 bytes max, and must be
# aligned with the 16-byte page intervals.  For instance, if you start writing
# at address 14, you can only write two bytes because byte 16 is the start of a
# new page.
ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 5)  # Set the number of bytes to transmit
ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 0)  # Set the number of bytes to receive

# Set the TX bytes.
numBytes = 5
aBytes = [0]  # Byte 0: Memory pointer = 0
# Create 4 new random numbers to write (aBytes[1-4]).
aBytes.extend([randrange(0, 256) for _ in range(4)])
ljm.eWriteNameByteArray(handle, "I2C_DATA_TX", numBytes, aBytes)

ljm.eWriteName(handle, "I2C_GO", 1)  # Do the I2C communications.

print("Write User Memory [0-3] = %s" %
      " ".join([("%.0f" % val) for val in aBytes[1:]]))

# Final read of EEPROM bytes 0-3 in the user memory area. We need a single I2C
# transmission that writes the address and then reads the data.
ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 1)  # Set the number of bytes to transmit
ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 4)  # Set the number of bytes to receive

# Set the TX bytes. We are sending 1 byte for the address.
numBytes = 1
aBytes = [0]  # Byte 0: Memory pointer = 0
ljm.eWriteNameByteArray(handle, "I2C_DATA_TX", numBytes, aBytes)

ljm.eWriteName(handle, "I2C_GO", 1)  # Do the I2C communications.

# Read the RX bytes.
numBytes = 4
# aBytes[0] to aBytes[3] will contain the data
aBytes = [0]*4
aBytes = ljm.eReadNameByteArray(handle, "I2C_DATA_RX", numBytes)

print("Read User Memory [0-3] = %s" %
      " ".join([("%.0f" % val) for val in aBytes]))

# Close handle
ljm.close(handle)
