"""
Demonstrates I2C communication using the LJM driver. The demonstration uses a
a LJTick-DAC connected to FIO0/FIO1, configures I2C settings, and reads, writes
and reads bytes from/to the EEPROM.

"""

from labjack import ljm
from random import randrange


# Open first found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")
#handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")


info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))


# Configure the I2C communication.
ljm.eWriteName(handle, "I2C_SDA_DIONUM", 1) # SDA pin number = 1 (FIO1)
ljm.eWriteName(handle, "I2C_SCL_DIONUM", 0) # SCL pin number = 0 (FIO0)

# Speed throttle is inversely proportional to clock frequency. 0 = max.
ljm.eWriteName(handle, "I2C_SPEED_THROTTLE", 0) # Speed throttle = 0

# Options bits:
#   bit0: Reset the I2C bus.
#   bit1: Restart w/o stop
#   bit2: Disable clock stretching.
ljm.eWriteName(handle, "I2C_OPTIONS", 0) # Options = 0

ljm.eWriteName(handle, "I2C_SLAVE_ADDRESS", 80) # Slave Address of the I2C chip = 80 (0x50)


# Initial read of EEPROM bytes 0-3 in the user memory area. We need a single I2C
# transmission that writes the chip's memory pointer and then reads the data.
ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 1) # Set the number of bytes to transmit
ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 4) # Set the number of bytes to receive

# Set the TX bytes. We are sending 1 byte for the address.
aNames = ["I2C_DATA_TX"]
aWrites = [ljm.constants.WRITE] # Indicates we are writing the values.
aNumValues = [1] # The number of bytes
aValues = [0] # Byte 0: Memory pointer = 0
ljm.eNames(handle, len(aNames), aNames, aWrites, aNumValues, aValues)

ljm.eWriteName(handle, "I2C_GO", 1) # Do the I2C communications.

# Read the RX bytes.
aNames = ["I2C_DATA_RX"]
aWrites = [ljm.constants.READ] # Indicates we are reading the values.
aNumValues = [4] # The number of bytes
# aValues[0] to aValues[3] will contain the data
aValues = [0]*4
aValues = ljm.eNames(handle, len(aNames), aNames, aWrites, aNumValues, aValues)

print("\nRead User Memory [0-3] = %s" % \
      " ".join([("%.0f"%val) for val in aValues]))


# Write EEPROM bytes 0-3 in the user memory area, using the page write
# technique.  Note that page writes are limited to 16 bytes max, and must be
# aligned with the 16-byte page intervals.  For instance, if you start writing
# at address 14, you can only write two bytes because byte 16 is the start of a
# new page.
ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 5) # Set the number of bytes to transmit
ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 0) # Set the number of bytes to receive

# Set the TX bytes.
aNames = ["I2C_DATA_TX"]
aWrites = [ljm.constants.WRITE] # Indicates we are writing the values.
aNumValues = [5] # The number of bytes
aValues = [0] # Byte 0: Memory pointer = 0
# Create 4 new random numbers to write (aValues[1-4]).
aValues.extend([randrange(0, 256) for _ in range(4)])
ljm.eNames(handle, len(aNames), aNames, aWrites, aNumValues, aValues)

ljm.eWriteName(handle, "I2C_GO", 1) # Do the I2C communications.

print("Write User Memory [0-3] = %s" % \
      " ".join([("%.0f"%val) for val in aValues[1:]]))


# Final read of EEPROM bytes 0-3 in the user memory area. We need a single I2C
# transmission that writes the address and then reads the data.
ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 1) # Set the number of bytes to transmit
ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 4) # Set the number of bytes to receive

# Set the TX bytes. We are sending 1 byte for the address.
aNames = ["I2C_DATA_TX"]
aWrites = [ljm.constants.WRITE] # Indicates we are writing the values.
aNumValues = [1] # The number of bytes
aValues = [0] # Byte 0: Memory pointer = 0
ljm.eNames(handle, len(aNames), aNames, aWrites, aNumValues, aValues)

ljm.eWriteName(handle, "I2C_GO", 1) # Do the I2C communications.

# Read the RX bytes.
aNames = ["I2C_DATA_RX"]
aWrites = [ljm.constants.READ] # Indicates we are reading the values.
aNumValues = [4] # The number of bytes
# aValues[0] to aValues[3] will contain the data
aValues = [0]*4
aValues = ljm.eNames(handle, 1, aNames, aWrites, aNumValues, aValues)

print("Read User Memory [0-3] = %s" % \
      " ".join([("%.0f"%val) for val in aValues]))


# Close handle
ljm.close(handle)
