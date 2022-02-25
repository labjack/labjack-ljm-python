"""
Demonstrates I2C communication using a LabJack. The demonstration uses an
SHT3X temperature and humidity sensor connected to FIO0/FIO1/FIO2 for the T7,
or FIO4/FIO5/FIO6 for the T4. A write command to set up single shot acquisition
is performed, then subsequently a read only transaction is performed to read
sensor data.

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
    I2C:
        https://labjack.com/support/datasheets/t-series/digital-io/i2c

"""
from time import sleep

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
    # Configure FIO4, FIO5, and FIO6 as digital I/O.
    ljm.eWriteName(handle, "DIO_INHIBIT", 0xFFF8F)
    ljm.eWriteName(handle, "DIO_ANALOG_ENABLE", 0x00000)

    # For the T4, using FIO4 and FIO5 for SCL and SDA pins. FIO0 to FIO3 are
    # reserved for analog inputs, and digital lines are required.
    ljm.eWriteName(handle, "I2C_SDA_DIONUM", 5)  # SDA pin number = 5 (FIO5)
    ljm.eWriteName(handle, "I2C_SCL_DIONUM", 4)  # SCL pin number = 4 (FIO4)
    # Use FIO6 for power by setting it to output high
    ljm.eWriteName(handle, "FIO6", 1)
else:
    # For the T7 and other devices, using FIO0 and FIO1 for the SCL and SDA
    # pins.
    ljm.eWriteName(handle, "I2C_SDA_DIONUM", 1)  # SDA pin number = 1 (FIO1)
    ljm.eWriteName(handle, "I2C_SCL_DIONUM", 0)  # SCL pin number = 0 (FIO0)
    # Use FIO2 for power by setting it to output high
    ljm.eWriteName(handle, "FIO2", 1)

# Speed throttle is inversely proportional to clock frequency. 0 = max.
ljm.eWriteName(handle, "I2C_SPEED_THROTTLE", 65000)  # Speed throttle = 65516 (~100 kHz)

# Options bits:
#     bit0: Reset the I2C bus.
#     bit1: Restart w/o stop
#     bit2: Disable clock stretching.
ljm.eWriteName(handle, "I2C_OPTIONS", 0)  # Options = 0

# The SHT3x address could be 0x44 or 0x45 depending on the address pin voltage
# A slave address of 0x44 indicates the ADDR pin is connected to a logic low
ljm.eWriteName(handle, "I2C_SLAVE_ADDRESS", 0x44)

# Start with a single shot write command to the SHT3x sensor.
ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 2)  # Set the number of bytes to transmit
ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 0)  # Set the number of bytes to receive

# Set the TX bytes
numBytes = 2
# 0x24 = clock stretching disabled, 0x00 = high repeatability
aBytes = [0x24, 0x00]
ljm.eWriteNameByteArray(handle, "I2C_DATA_TX", numBytes, aBytes)
ljm.eWriteName(handle, "I2C_GO", 1)  # Do the I2C communications.
 
# The sensor needs at least 15ms for the measurement. Wait 20ms
sleep(0.02)

# Do a read only transaction to obtain the readings
ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 0)  # Set the number of bytes to transmit
ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 6)  # Set the number of bytes to receive
ljm.eWriteName(handle, "I2C_GO", 1)  # Do the I2C communications.

# SHT3x sensors should always return 6 bytes for single shot acquisition: 
# [temp MSB, temp LSB, CRC, RH MSB, RH LSB, CRC]
numBytes = 6
aBytes = [0]*6
aBytes = ljm.eReadNameByteArray(handle, "I2C_DATA_RX", numBytes)
tempBin = aBytes[0]*256 + aBytes[1]
tempC = 175*tempBin / 65535 - 45
rhBin = aBytes[3]*256 + aBytes[4]
rh = 100*rhBin / 65535
print("tempC = %f degC, RH = %f%%\n" % (tempC, rh))

# Close handle
ljm.close(handle)
