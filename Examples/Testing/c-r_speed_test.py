"""
Performs LabJack operations in a loop and reports the timing statistics for the
operations.

"""

from labjack import ljm
from datetime import datetime
import timeit
import functools

def eNamesIteration(handle, numFrames, names, aWrites, aNumValues, aValues,
                    results):
    # Function for timit.Timer. Performs a eNames call to do LabJack operations.
    # Takes eNames parameters and a list for results which will be filled.
    del results[:]
    r = ljm.eNames(handle, numFrames, names, aWrites, aNumValues, aValues)
    results.extend(r)

# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
#handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))


numIterations = 1000 # Number of iterations to perform in the loop

# Analog input settings
numAIN = 1 # Number of analog inputs to read
rangeAIN = 10.0
resolutionAIN = 1

# Digital settings
readDigital = False
writeDigital = False

# Analog output settings
writeDACs = False

if numAIN > 0:
    # Configure analog input settings
    numFrames = 0
    names = []
    aValues = []
    for i in range(numAIN):
        numFrames += 2
        names.append("AIN%i_RANGE"%i)
        aValues.append(rangeAIN)
        names.append("AIN%i_RESOLUTION_INDEX"%i)
        aValues.append(resolutionAIN)

    ljm.eWriteNames(handle, numFrames, names, aValues)

# Initialize and configure eNames parameters for loop's eNames call
numFrames = 0
names = []
aWrites = []
aNumValues = []
aValues = []

# Add analog input reads (AIN 0 to numAIN-1)
for i in range(numAIN):
    numFrames += 1
    names.append("AIN%i"%i)
    aWrites.append(ljm.constants.READ)
    aNumValues.append(1)
    aValues.append(0)

if readDigital is True:
    # Add digital read
    numFrames += 1
    names.append("DIO_STATE")
    aWrites.append(ljm.constants.READ)
    aNumValues.append(1)
    aValues.append(0)

if writeDigital is True:
    # Add digital write
    numFrames += 1
    names.append("DIO_STATE")
    aWrites.append(ljm.constants.WRITE)
    aNumValues.append(1)
    aValues.append(0) #output-low

if writeDACs is True:
    # Add analog output writes (DAC0-1)
    for i in range(2):
        numFrames += 1
        names.append("DAC%i"%i)
        aWrites.append(ljm.constants.WRITE)
        aNumValues.append(1)
        aValues.append(0.0) #0.0 V


print("\nTest frames:")

for i in range(numFrames):
    if aWrites[i] == ljm.constants.READ:
        wrStr = "READ"
    else:
        wrStr = "WRITE"
    print("    %s %s" % (wrStr, names[i]))

print("\nBeginning %i iterations..." % numIterations)


# Initialize time variables
maxMS = 0
minMS = 0
totalMS = 0
results = []
t = timeit.Timer(functools.partial(eNamesIteration, handle, numFrames, names,
                                   aWrites, aNumValues, aValues, results))

# eNames loop
for i in range(numIterations):
    ttMS = t.timeit(number = 1)
    if minMS == 0:
        minMS = ttMS
    minMS = min(ttMS, minMS)
    maxMS = max(ttMS, maxMS)
    totalMS += ttMS

print("\n%i iterations performed:" % numIterations)
print("    Time taken: %.3f ms" % (totalMS * 1000))
print("    Average time per iteration: %.3f ms" %
      (totalMS/numIterations * 1000))
print("    Min / Max time for one iteration: %.3f ms / %.3f ms" % \
        (minMS*1000, maxMS*1000))

print("\nLast eNames results: ")
for i in range(numFrames):
    if aWrites[i] == ljm.constants.READ:
        wrStr = "READ"
    else:
        wrStr = "WRITE"
    print("    %s %s value : %f" % (names[i], wrStr, results[i]))

# Close handle
ljm.close(handle)
