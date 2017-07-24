"""
Demonstrates 1-wire usage with a LabJack. For more information on the registers
and settings, refer to the 1-wire documentation in the device datasheet.

"""
from labjack import ljm


""" Constants """
# 1-wire function constants
SEARCH_FUNC = 0xF0
SKIP_FUNC = 0xCC
MATCH_FUNC = 0x55
READ_FUNC = 0x33

""" Functions """

# Performs I2C searches to find the roms. Configure ONEWIRE_DQ_DIONUM
# beforehand for the LabJack DIO number to search on. Returns a list of roms.
# A rom is a tuple:
# (rom_num_hi, rom_num_lo)
# For example, a two rom list:
# [(486539269, 2425177896), (4278190080, 615328802)]
def performROMSearch():
    # Perform search write
    numFrames = 4
    aNamesSrch = [0]*numFrames
    aNamesSrch[0] = "ONEWIRE_PATH_H"
    aNamesSrch[1] = "ONEWIRE_PATH_L"
    aNamesSrch[2] = "ONEWIRE_FUNCTION"
    aNamesSrch[3] = "ONEWIRE_GO"
    aValuesSrch = [0]*numFrames
    aValuesSrch[0] = 0  # Path H: 0
    aValuesSrch[1] = 0  # Path L: 0
    aValuesSrch[2] = SEARCH_FUNC  # Function: Search (0xF0)
    aValuesSrch[3] = 1  # Go: 1 (perform transaction)

    # Get results read
    aNamesRes = [0]*numFrames
    aNamesRes[0] = "ONEWIRE_ROM_BRANCHS_FOUND_H"
    aNamesRes[1] = "ONEWIRE_ROM_BRANCHS_FOUND_L"
    aNamesRes[2] = "ONEWIRE_SEARCH_RESULT_H"
    aNamesRes[3] = "ONEWIRE_SEARCH_RESULT_L"

    roms = []
    while(True):
        print(aValuesSrch)
        # Perform search
        ljm.eWriteNames(handle, numFrames, aNamesSrch, aValuesSrch)
        # Get results of search
        aValuesRes = ljm.eReadNames(handle, numFrames, aNamesRes)

        rom = (int(aValuesRes[2]), int(aValuesRes[3]))  # ONEWIRE_SEARCH_RESULT_H, ONEWIRE_SEARCH_RESULT_L
        roms.extend([rom])

        branch = (int(aValuesRes[0]), int(aValuesRes[1])) # ONEWIRE_ROM_BRANCHS_FOUND_H, ONEWIRE_ROM_BRANCHS_FOUND_L
        if branch[0] == 0 and branch[1] == 0:
            # Branch path is zero. Reached the end and stopping
            break

        # Update the path for next search
        aValuesSrch[0] = branch[0]  # Path H
        aValuesSrch[1] = branch[1]  # Path L
        print("  " + str(aValuesRes)) 
    return roms

""" Main """

# Open first found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
#handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
#handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
#handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))


# Configure 1-wire settings
dqDIO = 8  # DIO8 = EIO0
dpuDIO = 0  # DIO0 = FIO0 (Not using)
options = 0

numFrames = 3
aNames = [0]*numFrames
aNames[0] = "ONEWIRE_DQ_DIONUM"
aNames[1] = "ONEWIRE_DPU_DIONUM"
aNames[2] = "ONEWIRE_OPTIONS"
aValues = [0]*numFrames
aValues[0] = dqDIO  # Data line
aValues[1] = dpuDIO  # Dynamic pullup control line
aValues[2] = options  # Options
ljm.eWriteNames(handle, numFrames, aNames, aValues)

# Search for 1-wire ROMs.
roms = performROMSearch()

print("Discovered the following rom IDs through DIO%d" % dqDIO)
for rom in roms:
    print("  %d" % ((int(rom[0]) << 32) + int(rom[1])))

# Settings the rom to use.
roms = roms[0]
print("Using rom with ID " % ((int(rom[0]) << 32) + int(rom[1])))

'''

# Setup and call eWriteNames to write values to the LabJack.
numFrames = 2
names = ["DAC0", "TEST_UINT16"]
aValues = [2.5, 12345]  # [2.5 V, 12345]
ljm.eWriteNames(handle, numFrames, names, aValues)

print("\neWriteNames: ")
for i in range(numFrames):
    print("    Name - %s, value : %f" % (names[i], aValues[i]))
'''

# Close handle
ljm.close(handle)