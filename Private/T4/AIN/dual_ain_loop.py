"""
Demonstrates reading 2 analog inputs (AINs) in a loop from a LabJack.

"""
from datetime import datetime
import sys
import time
from threading import Timer

from labjack import ljm

class RepeatingTimer():
    # Not very accurate
    def __init__(self, interval, repeats, function, *args, **kwargs):
        # Add value checks
        self.interval = interval
        self.repeats = repeats
        self.repeatsCurrent = repeats
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self._timer = None
        self._isTimerRunning = False  # Is Timer function running
        self.isRunning = False  # Is this class running
        self.lastTime = datetime.now()

    def _run(self):
        diff = datetime.now() - self.lastTime
        diffSec = diff.days*86400 + diff.seconds + diff.microseconds/1000000.0
        print("Actual interval (sec): %s" % (diffSec))
        print("Error (milliseconds): %s" % ((self.interval - diffSec)*1000))
        self.lastTime = datetime.now()

        self._isTimerRunning = False
        self._start()  # Next interval


        self.function(*self.args, **self.kwargs)

    def start(self):
        self.isRunning = True
        self._start()

    def _start(self, interval):
        if self.isRunning and not self._isTimerRunning:
            if self.repeats is not "inf":
                self.repeats -= self.repeats
                if self.repeats <= 0:  # Check logic later
                    self.isRunning = false
                    return  # Done
            self._timer = Timer(interval, self._run)
            self._timer.start()
            self._isTimerRunning = True
        elif self._isTimerRunning:
            print("Timer overlap")

    def cancel(self):
        self._timer.cancel()
        self.isRunning = False
        self._isTimerRunning = False
        


def doReading(handle):
    numFrames = 2
    names = ["AIN0", "AIN1"]
    results = ljm.eReadNames(handle, numFrames, names)
    print("\n%s" % datetime.now())
    print("AIN0 : %f V, AIN1 : %f V" % (results[0], results[1]))

loopMessage = ""
if len(sys.argv) > 1:
    # An argument was passed. The first argument specifies how many times to
    # loop.
    try:
        loopAmount = int(sys.argv[1])
    except:
        raise Exception("Invalid first argument \"%s\". This specifies how many"
                        " times to loop and needs to be a number." %
                        str(sys.argv[1]))
else:
    # An argument was not passed. Loop an infinite amount of times.
    loopAmount = "inf"
    loopMessage = " Press Ctrl+C to stop."

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

# Setup and call eWriteNames to configure AIN0 and AIN1 on the LabJack.
numFrames = 8
# AIN0 and AIN1:
#   Negative channel = single ended (199)
#   Range: +/-10.0 V (10.0). T4 note: Only AIN0-AIN3 can support +/-10 V range.
#   Resolution index = Default (0)
#   Settling, in microseconds = Auto (0)
names = ["AIN0_NEGATIVE_CH", "AIN0_RANGE", "AIN0_RESOLUTION_INDEX", "AIN0_SETTLING_US",
         "AIN1_NEGATIVE_CH", "AIN1_RANGE", "AIN1_RESOLUTION_INDEX", "AIN1_SETTLING_US"]
aValues = [199, 10.0, 0, 0,
           199, 10.0, 0, 0]

ljm.eWriteNames(handle, numFrames, names, aValues)

print("\nSet configuration:")
for i in range(numFrames):
    print("    %s : %f" % (names[i], aValues[i]))

# Read AIN0 and AIN1 from the LabJack with eReadNames in a loop.
numFrames = 2
names = ["AIN0", "AIN1"]

print("\nStarting %s read loops.%s\n" % (str(loopAmount), loopMessage))
delay = 1.0  # Delay between readings (in seconds)
"""

i = 0
while True:
    try:
        results = ljm.eReadNames(handle, numFrames, names)
        print("AIN0 : %f V, AIN1 : %f V" % (results[0], results[1]))
        time.sleep(delay)
        if loopAmount is not "infinite":
            i = i + 1
            if i >= loopAmount:
                break
    except KeyboardInterrupt:
        break
    except Exception:
        import sys
        print(sys.exc_info()[1])
        break
"""
try:
    pass
except KeyboardInterrupt:
    pass
except Exception:
    print(sys.exc_info()[1])
    pass

timer = RepeatingTimer(delay, loopAmount, doReading, handle)
timer.start()
while timer.isRunning:
    time.sleep(0.10)

# Close handle
ljm.close(handle)
