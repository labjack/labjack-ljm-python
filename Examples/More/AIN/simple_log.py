"""
This example is meant to be paired with LabJack's other examples:
https://labjack.com/support/software/examples/ljm/python
This example demonstrates reading a single analog input (AIN0) 
from a LabJack 10 times (at 10Hz or with a 100ms delay between
samples) and logging that data to a .csv file.

Docs for datetime: https://docs.python.org/3/library/datetime.html
A few relevant stackoverflow examples:
https://stackoverflow.com/questions/3316882/how-do-i-get-a-string-format-of-the-current-date-time-in-python
Docs for os (how to get the CWD):
https://docs.python.org/3/library/os.html
Docs for os.path (how to join paths):
https://docs.python.org/3/library/os.path.html#module-os.path
"""
from labjack import ljm

import datetime
import os
import sys
import time


# Open first found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
#handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
#handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
#handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

info = ljm.getHandleInfo(handle)
print("\nOpened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Setup and call eReadName to read from AIN0 on the LabJack.
name = "AIN0"
numIterations = 10
rate = 100 # in ms
rateUS = rate*1000


# Get the current time to build a time-stamp.
appStartTime = datetime.datetime.now()
# startTimeStr = appStartTime.isoformat(timespec='milliseconds')
startTimeStr = appStartTime.strftime("%Y/%m/%d %I:%M:%S%p")
timeStr = appStartTime.strftime("%Y_%m_%d-%I_%M_%S%p")

# Get the current working directory
cwd = os.getcwd()

# Build a file-name and the file path.
fileName = timeStr + "-%s-Example.csv"%(name)
filePath = os.path.join(cwd, fileName)

# Open the file & write a header-line
f = open(filePath, 'w')
f.write("Time Stamp, Duration/Jitter (ms), %s" %(name))

# Print some program-initialization information
print("The time is: %s" %(startTimeStr))
print("Reading %s %i times and saving data to the file:\n - %s\n" %(name, numIterations, filePath))

# Prepare final variables for program execution
intervalHandle = 0
ljm.startInterval(intervalHandle, rateUS)
curIteration = 0
numSkippedIntervals = 0

lastTick = ljm.getHostTick()
duration = 0

while curIteration < numIterations:
	try:
		numSkippedIntervals = ljm.waitForNextInterval(intervalHandle)
		curTick = ljm.getHostTick()
		duration = (curTick-lastTick)/1000
		curTime = datetime.datetime.now()
		curTimeStr = curTime.strftime("%Y/%m/%d %I:%M:%S%p")

		# Read AIN0
		result = ljm.eReadName(handle, name)

		# Print results
		print("%s reading: %f V, duration: %0.1f ms, skipped intervals: %i" % (name, result, duration, numSkippedIntervals))
		f.write("%s, %0.1f, %0.3f\r\n" %(curTimeStr, duration, result))
		lastTick = curTick
		curIteration = curIteration + 1
	except KeyboardInterrupt:
		break
	except Exception:
		import sys
		print(sys.exc_info()[1])
		break

print("\nFinished!")

#Get the final time
appEndTime = datetime.datetime.now()
# endTimeStr = appEndTime.isoformat(timespec='milliseconds')
endTimeStr = appStartTime.strftime("%Y/%m/%d %I:%M:%S%p")
print("The final time is: %s" %(endTimeStr))

# Close file
f.close()

# Close handles
ljm.cleanInterval(intervalHandle)
ljm.close(handle)
