"""
Performs LabJack operations in a loop and reports the timing statistics for the
operations.

"""
from datetime import datetime
import functools
import timeit

from labjack import ljm


def eNamesIteration(handle, numFrames, aNames, aWrites, aNumValues, aValues,
                    results):
    """Function for timit.Timer. Performs an eNames call to do LabJack
    operations. Takes eNames parameters and a list for results which
    will be filled.

    """
    del results[:]
    r = ljm.eNames(handle, numFrames, aNames, aWrites, aNumValues, aValues)
    results.extend(r)


def eAddressesIteration(handle, numFrames, aAddresses, aTypes, aWrites,
                        aNumValues, aValues, results):
    """Function for timit.Timer. Performs an eAddresses call to do
    LabJack operations. Takes eAddresses parameters and a list for
    results which will be filled.

    """
    del results[:]
    r = ljm.eAddresses(handle, numFrames, aAddresses, aTypes, aWrites,
                       aNumValues, aValues)
    results.extend(r)


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

numIterations = 1000  # Number of iterations to perform in the loop

# Analog input settings
numAIN = 1  # Number of analog inputs to read
resolutionAIN = 1

# Digital settings
readDigital = False
writeDigital = False

# Analog output settings
writeDACs = False

# Use eAddresses (True) or eNames (False) in the operations loop. eAddresses
# is faster than eNames.
useAddresses = True

# Device specific configuration
if deviceType == ljm.constants.dtT4:
    # T4 analog input configuration
    rangeAINHV = 10.0  # HV channels range
    rangeAINLV = 2.5  # LV channels range

    # Configure the channels to analog input or digital I/O
    # Update all digital I/O channels. b1 = Ignored. b0 = Affected.
    dioInhibit = 0x00000  # (b00000000000000000000)
    # Set AIN 0 to numAIN-1 as analog inputs (b1), the rest as digital I/O (b0).
    dioAnalogEnable = (2 ** numAIN) - 1
    ljm.eWriteNames(handle, 2,
                    ["DIO_INHIBIT", "DIO_ANALOG_ENABLE"],
                    [dioInhibit, dioAnalogEnable])
    if writeDigital is True:
        # Update only digital I/O channels in future digital write calls.
        # b1 = Ignored. b0 = Affected.
        dioInhibit = dioAnalogEnable
        ljm.eWriteName(handle, "DIO_INHIBIT", dioInhibit)
else:
    # T7 and other devices analog input configuration
    rangeAIN = 10.0

if numAIN > 0:
    # Configure analog input settings
    numFrames = 0
    aNames = []
    aValues = []
    for i in range(numAIN):
        numFrames += 2
        aNames.append("AIN%i_RANGE" % i)
        if deviceType == ljm.constants.dtT4:
            if i < 4:
                # Set the HV range
                aValues.append(rangeAINHV)
            else:
                # Set the LV range
                aValues.append(rangeAINLV)
        else:
            aValues.append(rangeAIN)
        aNames.append("AIN%i_RESOLUTION_INDEX" % i)
        aValues.append(resolutionAIN)
    ljm.eWriteNames(handle, numFrames, aNames, aValues)

# Initialize and configure eNames parameters for loop's eNames call
numFrames = 0
aNames = []
aWrites = []
aNumValues = []
aValues = []

# Add analog input reads (AIN 0 to numAIN-1)
for i in range(numAIN):
    numFrames += 1
    aNames.append("AIN%i" % i)
    aWrites.append(ljm.constants.READ)
    aNumValues.append(1)
    aValues.append(0)

if readDigital is True:
    # Add digital read
    numFrames += 1
    aNames.append("DIO_STATE")
    aWrites.append(ljm.constants.READ)
    aNumValues.append(1)
    aValues.append(0)

if writeDigital is True:
    # Add digital write
    numFrames += 1
    aNames.append("DIO_STATE")
    aWrites.append(ljm.constants.WRITE)
    aNumValues.append(1)
    aValues.append(0)  # output-low

if writeDACs is True:
    # Add analog output writes (DAC0-1)
    for i in range(2):
        numFrames += 1
        aNames.append("DAC%i" % i)
        aWrites.append(ljm.constants.WRITE)
        aNumValues.append(1)
        aValues.append(0.0)  # 0.0 V

# Make lists of addresses and data types for eAddresses.
aAddresses, aTypes = ljm.namesToAddresses(numFrames, aNames)

print("\nTest frames:")
for i in range(numFrames):
    if aWrites[i] == ljm.constants.READ:
        wrStr = "READ"
    else:
        wrStr = "WRITE"
    print("    %s %s (%s)" % (wrStr, aNames[i], aAddresses[i]))

print("\nBeginning %i iterations..." % numIterations)

# Initialize time variables
maxMS = 0
minMS = 0
totalMS = 0
results = []
t = None
if useAddresses:
    t = timeit.Timer(functools.partial(eAddressesIteration, handle, numFrames,
                                       aAddresses, aTypes, aWrites, aNumValues,
                                       aValues, results))
else:
    t = timeit.Timer(functools.partial(eNamesIteration, handle, numFrames,
                                       aNames, aWrites, aNumValues, aValues,
                                       results))

# eAddresses or eNames loop
for i in range(numIterations):
    ttMS = t.timeit(number=1)
    if minMS == 0:
        minMS = ttMS
    minMS = min(ttMS, minMS)
    maxMS = max(ttMS, maxMS)
    totalMS += ttMS

print("\n%i iterations performed:" % numIterations)
print("    Time taken: %.3f ms" % (totalMS * 1000))
print("    Average time per iteration: %.3f ms" %
      (totalMS / numIterations * 1000))
print("    Min / Max time for one iteration: %.3f ms / %.3f ms" %
      (minMS * 1000, maxMS * 1000))
if useAddresses:
    print("\nLast eAddresses results: ")
else:
    print("\nLast eNames results: ")
for i in range(numFrames):
    if aWrites[i] == ljm.constants.READ:
        wrStr = "READ"
    else:
        wrStr = "WRITE"
    print("    %s (%s) %s value : %f" % (aNames[i], aAddresses[i], wrStr,
                                         results[i]))

# Close handle
ljm.close(handle)
