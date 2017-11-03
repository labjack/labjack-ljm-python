"""
Demonstrates SPI communication.

You can short MOSI to MISO for testing.

T7:
    MOSI    FIO2
    MISO    FIO3
    CLK     FIO0
    CS      FIO1

T4:
    MOSI    FIO6
    MISO    FIO7
    CLK     FIO4
    CS      FIO5

If you short MISO to MOSI, then you will read back the same bytes that you
write.  If you short MISO to GND, then you will read back zeros.  If you
short MISO to VS or leave it unconnected, you will read back 255s.

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

if deviceType == ljm.constants.dtT4:
    # Configure FIO4 to FIO7 as digital I/O.
    ljm.eWriteName(handle, "DIO_INHIBIT", 0xFFF0F)
    ljm.eWriteName(handle, "DIO_ANALOG_ENABLE", 0x00000)

    # Setting CS, CLK, MISO, and MOSI lines for the T4. FIO0 to FIO3 are
    # reserved for analog inputs, and SPI requires digital lines.
    ljm.eWriteName(handle, "SPI_CS_DIONUM", 5)  # CS is FIO5
    ljm.eWriteName(handle, "SPI_CLK_DIONUM", 4)  # CLK is FIO4
    ljm.eWriteName(handle, "SPI_MISO_DIONUM", 7)  # MISO is FIO7
    ljm.eWriteName(handle, "SPI_MOSI_DIONUM", 6)  # MOSI is FIO6
else:
    # Setting CS, CLK, MISO, and MOSI lines for the T7 and other devices.
    ljm.eWriteName(handle, "SPI_CS_DIONUM", 1)  # CS is FIO1
    ljm.eWriteName(handle, "SPI_CLK_DIONUM", 0)  # CLK is FIO0
    ljm.eWriteName(handle, "SPI_MISO_DIONUM", 3)  # MISO is FIO3
    ljm.eWriteName(handle, "SPI_MOSI_DIONUM", 2)  # MOSI is FIO2

# Selecting Mode CPHA=1 (bit 0), CPOL=1 (bit 1)
ljm.eWriteName(handle, "SPI_MODE", 3)

# Speed Throttle:
# Valid speed throttle values are 1 to 65536 where 0 = 65536.
# Configuring Max. Speed (~800 kHz) = 0
ljm.eWriteName(handle, "SPI_SPEED_THROTTLE", 0)

# SPI_OPTIONS:
# bit 0:
#     0 = Active low clock select enabled
#     1 = Active low clock select disabled.
# bit 1:
#     0 = DIO directions are automatically changed
#     1 = DIO directions are not automatically changed.
# bits 2-3: Reserved
# bits 4-7: Number of bits in the last byte. 0 = 8.
# bits 8-15: Reserved

# Enabling active low clock select pin
ljm.eWriteName(handle, "SPI_OPTIONS", 0)

# Read back and display the SPI settings
aNames = ["SPI_CS_DIONUM", "SPI_CLK_DIONUM", "SPI_MISO_DIONUM",
          "SPI_MOSI_DIONUM", "SPI_MODE", "SPI_SPEED_THROTTLE",
          "SPI_OPTIONS"]
aValues = [0]*len(aNames)
numFrames = len(aNames)
aValues = ljm.eReadNames(handle, numFrames, aNames)

print("\nSPI Configuration:")
for i in range(numFrames):
    print("  %s = %0.0f" % (aNames[i],  aValues[i]))

# Write(TX)/Read(RX) 4 bytes
numBytes = 4
ljm.eWriteName(handle, "SPI_NUM_BYTES", numBytes)

# Write the bytes
dataWrite = []
dataWrite.extend([randrange(0, 256) for _ in range(numBytes)])
ljm.eWriteNameByteArray(handle, "SPI_DATA_TX", len(dataWrite), dataWrite)
ljm.eWriteName(handle, "SPI_GO", 1)  # Do the SPI communications

# Display the bytes written
print("")
for i in range(numBytes):
    print("dataWrite[%i] = %0.0f" % (i, dataWrite[i]))

# Read the bytes
dataRead = ljm.eReadNameByteArray(handle, "SPI_DATA_RX", numBytes)
ljm.eWriteName(handle, "SPI_GO", 1)

# Display the bytes read
print("")
for i in range(numBytes):
    print("dataRead[%i]  = %0.0f" % (i, dataRead[i]))

# Close handle
ljm.close(handle)
