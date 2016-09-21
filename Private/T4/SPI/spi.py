"""
Demonstrates SPI communication.

You can short MOSI to MISO for testing.

MOSI    FIO6
MISO    FIO7
CLK     FIO4
CS      FIO5

If you short MISO to MOSI, then you will read back the same bytes that you
write.  If you short MISO to GND, then you will read back zeros.  If you
short MISO to VS or leave it unconnected, you will read back 255s.

"""

from labjack import ljm
from random import randrange

# Open first found LabJack
handle = ljm.openS("T4", "ANY", "ANY")
#handle = ljm.open(ljm.constants.dtT4, ljm.constants.ctANY, "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

cs = 5  # CS is FIO5
clk = 4  # CLK is FIO4
miso = 7  # MISO is FIO7
mosi = 6  # MOSI is FIO6

# Set CS, CLK, MISO and MOSI lines
ljm.eWriteName(handle, "SPI_CS_DIONUM", cs)
ljm.eWriteName(handle, "SPI_CLK_DIONUM", clk)
ljm.eWriteName(handle, "SPI_MISO_DIONUM", miso)
ljm.eWriteName(handle, "SPI_MOSI_DIONUM", mosi)

# Selecting Mode CPHA=1 (bit 1), CPOL=1 (bit 2)
ljm.eWriteName(handle, "SPI_MODE", 3)

# Speed Throttle: Max. Speed (~ 1 MHz) = 0
ljm.eWriteName(handle, "SPI_SPEED_THROTTLE", 0)

# Options
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

print("SPI Configuration:")
for i in range(numFrames):
    print("  %s = %0.0f" % (aNames[i],  aValues[i]))


# Write(TX)/Read(RX) 4 bytes
numBytes = 4;
ljm.eWriteName(handle, "SPI_NUM_BYTES", numBytes)


# Write the bytes
dataWrite = []
dataWrite.extend([randrange(0, 256) for _ in range(numBytes)])
aNames = ["SPI_DATA_TX"]
aWrites = [ljm.constants.WRITE]
aNumValues = [numBytes];
dataWrite = ljm.eNames(handle, 1, aNames, aWrites, aNumValues, dataWrite)

ljm.eWriteName(handle, "SPI_GO", 1) # Do the SPI communications

# Display the bytes written
print("");
for i in range(numBytes):
    print("dataWrite[%i] = %0.0f" % (i, dataWrite[i]))


# Read the bytes
dataRead = [0]*numBytes
aNames = ["SPI_DATA_RX"]
aWrites = [ljm.constants.READ]
aNumValues = [numBytes];
dataRead = ljm.eNames(handle, 1, aNames, aWrites, aNumValues, dataRead)
ljm.eWriteName(handle, "SPI_GO", 1)

# Display the bytes read
print("")
for i in range(numBytes):
    print("dataRead[%i] = %0.0f" % (i, dataRead[i]))

# Close handle
ljm.close(handle)
