"""
Performs LabJack operations in a loop and reports the timing statistics for the
operations.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    Single Value Functions (such as eWriteName):
        https://labjack.com/support/software/api/ljm/function-reference/single-value-functions
    Multiple Value Functions (such as eWriteNames, eNames and eAddresses):
        https://labjack.com/support/software/api/ljm/function-reference/multiple-value-functions

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Digital I/O:
        https://labjack.com/support/datasheets/t-series/digital-io
    Analog Inputs:
        https://labjack.com/support/datasheets/t-series/ain

Note:
    Our Python interfaces throw exceptions when there are any issues with
    device communications that need addressed. Many of our examples will
    terminate immediately when an exception is thrown. The onus is on the API
    user to address the cause of any exceptions thrown, and add exception
    handling when appropriate. We create our own exception classes that are
    derived from the built-in Python Exception class and can be caught as such.
    For more information, see the implementation in our source code and the
    Python standard documentation.
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
#handle = ljm.openS("T8", "ANY", "ANY")  # T8 device, Any connection, Any identifier
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
rangeAIN = 10.0  # T7/T8 AIN range. 10 = 10.0 V (T7) or 11.0 V (T8).
resolutionAIN = 1
samplingRateAIN = 40000  # Analog input sampling rate in Hz. T8 only.

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

if numAIN > 0:
    # Configure analog input settings
    numFrames = 0
    aNames = []
    aValues = []

    if deviceType == ljm.constants.dtT8:
        # Configure the T8 analog input resolution index, sampling rate and
        # range settings.
        numFrames = 2 + max(0, numAIN)

        # The T8 can only set the global resolution index.
        aNames.append("AIN_ALL_RESOLUTION_INDEX")
        aValues.append(resolutionAIN)

        # When setting a resolution index other than 0 (auto), set a valid
        # sample rate for the resolution.
        aNames.append("AIN_SAMPLING_RATE_HZ")
        aValues.append(samplingRateAIN)

        for i in range(numAIN):
            aNames.append("AIN%i_RANGE" % i)
            aValues.append(rangeAIN)
    elif deviceType == ljm.constants.dtT4:
        # Configure T4 analog input input resolution index.
        # Range is not applicable.
        numFrames = max(0, numAIN)
        for i in range(numAIN):
            aNames.append("AIN%d_RESOLUTION_INDEX" % i)
            aValues.append(resolutionAIN)
    else:
        # Configure T7 analog input resolution index and range settings.
        numFrames = max(0, numAIN * 2)
        for i in range(numAIN):
            aNames.append("AIN%d_RESOLUTION_INDEX" % i)
            aValues.append(resolutionAIN)
            aNames.append("AIN%d_RANGE" % i)
            aValues.append(rangeAIN)

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
    if deviceType != ljm.constants.dtT8 or i == 0:
        # For the T7 and T4 analog inputs, and the first T8 analog input,
        # use the the AIN# registers.
        aNames.append("AIN%i" % i)
    else:
        # For the T8 and its remaining analog inputs, use the AIN#_CAPTURE
        # registers for simultaneous readings.
        aNames.append("AIN%i_CAPTURE" % i)
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
