"""
Demonstrates reading 2 analog inputs (AINs) in a loop from a LabJack.

"""

from labjack import ljm
import time
import sys

# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
#handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Setup and call eWriteNames to configure AINs on the LabJack.
numFrames = 6
names = ["AIN0_NEGATIVE_CH", "AIN0_RANGE", "AIN0_RESOLUTION_INDEX",
         "AIN1_NEGATIVE_CH", "AIN1_RANGE", "AIN1_RESOLUTION_INDEX"]
aValues = [199, 10, 0,
           199, 10, 0]
ljm.eWriteNames(handle, numFrames, names, aValues)

print("\nSet configuration:")
for i in range(numFrames):
    print("    %s : %f" % (names[i], aValues[i]))

# Setup and call eReadNames to read AINs from the LabJack.
numFrames = 2
names = ["AIN0", "AIN1"]

s = ""
if len(sys.argv) > 1:
    #An argument was passed. The first argument specfies how many times to loop.
    try:
        loopAmount = int(sys.argv[1])
    except:
        raise Exception("Invalid first argument \"%s\". This specifies how many " \
                        "times to loop and needs to be a number." % str(sys.argv[1]))
else:
    #An argument was not passed. Loop an infinite amount of times.
    loopAmount = float("inf")
    s = " Press Ctrl+C to stop."

print("\nStarting %s read loops.%s" % (str(loopAmount), s))
delay = 1 #delay between readings (in sec)
i = 0
while i < loopAmount:
    try:
        results = ljm.eReadNames(handle, numFrames, names)
        print("\nAIN0 : %f V, AIN1 : %f V" % (results[0], results[1]))
        time.sleep(delay)
        i = i + 1
    except KeyboardInterrupt:
        break
    except Exception:
        import sys
        print(sys.exc_info()[1])
        break

# Close handle
ljm.close(handle)
