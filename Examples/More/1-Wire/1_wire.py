"""
Demonstrates 1-Wire communication with a DS1822 sensor and a LabJack. This
demonstration:
  - Searches for and displays the ROM ID and path of the connected 1-Wire device
    on EIO0.
  - Reads temperature from a DS1822 sensor.

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

if deviceType == ljm.constants.dtT4:
    # Configure EIO0 as digital I/O.
    ljm.eWriteName(handle, "DIO_INHIBIT", 0xFFEFF)
    ljm.eWriteName(handle, "DIO_ANALOG_ENABLE", 0x00000)


# Configure 1-Wire pins and options.
dqPin = 8  # EIO8
dpuPin = 0  # Not used
options = 0  # bit 2 = 0 (DPU disabled), bit 3 = 0 (DPU polarity low, ignored)
aNames = ["ONEWIRE_DQ_DIONUM",
          "ONEWIRE_DPU_DIONUM",
          "ONEWIRE_OPTIONS"]
aValues = [dqPin,
           dpuPin,
           options]
ljm.eWriteNames(handle, len(aNames), aNames, aValues)
print("\nUsing the DS1822 sensor with 1-Wire communications.")
print("  DQ pin = %d" % dqPin)
print("  DPU pin = %d" % dpuPin)
print("  Options  = %d" % options)

# Search for the 1-Wire device and get its ROM ID and path.
function = 0xF0  # Search
numTX = 0
numRX = 0
aNames = ["ONEWIRE_FUNCTION",
          "ONEWIRE_NUM_BYTES_TX",
          "ONEWIRE_NUM_BYTES_RX"]
aValues = [function,
           numTX,
           numRX]
ljm.eWriteNames(handle, len(aNames), aNames, aValues)
ljm.eWriteName(handle, "ONEWIRE_GO", 1)
aNames = ["ONEWIRE_SEARCH_RESULT_H",
          "ONEWIRE_SEARCH_RESULT_L",
          "ONEWIRE_ROM_BRANCHS_FOUND_H",
          "ONEWIRE_ROM_BRANCHS_FOUND_L"]
aValues = ljm.eReadNames(handle, len(aNames), aNames)
romH = aValues[0]
romL = aValues[1]
rom = (int(romH)<<8) + int(romL)
pathH = aValues[2]
pathL = aValues[3]
path = (int(pathH)<<8) + int(pathL)
print("  ROM ID = %d" % rom)
print("  Path = %d" % path)

# Setup the binary temperature read.
print("Setup the binary temperature read.")
function = 0x55  # Match
numTX = 1
dataTX = [0x44]  # 0x44 = DS1822 Convert T command
numRX = 0
aNames = ["ONEWIRE_FUNCTION",
          "ONEWIRE_NUM_BYTES_TX",
          "ONEWIRE_NUM_BYTES_RX",
          "ONEWIRE_ROM_MATCH_H",
          "ONEWIRE_ROM_MATCH_L",
          "ONEWIRE_PATH_H",
          "ONEWIRE_PATH_L"]
aValues = [function,
           numTX,
           numRX,
           romH,
           romL,
           pathH,
           pathL]
ljm.eWriteNames(handle, len(aNames), aNames, aValues)
ljm.eWriteNameByteArray(handle, "ONEWIRE_DATA_TX", numTX, dataTX)
ljm.eWriteName(handle, "ONEWIRE_GO", 1)

# Read the binary temperature.
print("Read the binary temperature.")
function = 0x55  # Match
numTX = 1
dataTX = [0xBE]  # 0xBE = DS1822 Read scratchpad command
numRX = 2
aNames = ["ONEWIRE_FUNCTION",
          "ONEWIRE_NUM_BYTES_TX",
          "ONEWIRE_NUM_BYTES_RX",
          "ONEWIRE_ROM_MATCH_H",
          "ONEWIRE_ROM_MATCH_L",
          "ONEWIRE_PATH_H",
          "ONEWIRE_PATH_L"]
aValues = [function,
           numTX,
           numRX,
           romH,
           romL,
           pathH,
           pathL]
ljm.eWriteNames(handle, len(aNames), aNames, aValues)
ljm.eWriteNameByteArray(handle, "ONEWIRE_DATA_TX", numTX, dataTX)
ljm.eWriteName(handle, "ONEWIRE_GO", 1)
dataRX = ljm.eReadNameByteArray(handle, "ONEWIRE_DATA_RX", numRX)
temperature = (int(dataRX[0]) + (int(dataRX[1])<<8))
if temperature == 0x0550:
    print("The DS1822 power on reset value is 85 C.")
    print("Read again get the real temperature.")
else:
    temperature = temperature * 0.0625
    print("Temperature = %f C" % temperature);

ljm.close(handle)
