"""
Demonstrates reading a single analog input (AIN0) from a LabJack at a rate of
10 samples per second and logging that data to a .csv file.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    eReadName:
        https://labjack.com/support/software/api/ljm/function-reference/ljmereadname

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Analog Inputs:
        https://labjack.com/support/datasheets/t-series/ain

Python:
    datetime:
        https://docs.python.org/3/library/datetime.html
    StackOverflow Example:
        https://stackoverflow.com/questions/3316882/how-do-i-get-a-string-format-of-the-current-date-time-in-python
    os (how to get the CWD and how to join paths):
        https://docs.python.org/3/library/os.html
        https://docs.python.org/3/library/os.path.html#module-os.path
"""
import datetime
import os
import sys
import time

from labjack import ljm


# Open the first found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
#handle = ljm.openS("T8", "ANY", "ANY")  # T8 device, Any connection, Any identifier
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
rate = 100  # in ms
rateUS = rate*1000
timestampFormat = "%Y-%m-%d %I:%M:%S.%f"  # year-month-day hour:minute:second.microsecond

# Get the current time to build a time-stamp.
appStartTime = datetime.datetime.now()
#startTimeStr = appStartTime.isoformat(timespec='milliseconds')
startTimeStr = appStartTime.strftime(timestampFormat)

# Reformat the start timestamp so that it can be used in a file name.
fileDateTime = appStartTime.strftime("%Y-%m-%d_%I-%M-%S")

# Get the current working directory
cwd = os.getcwd()

# Build a file-name and the file path.
fileName = "%s-%s-Example.csv" % (fileDateTime, name)
filePath = os.path.join(cwd, fileName)

# Open the file and write a header line.
f = open(filePath, 'w')
f.write("Timestamp, Duration/Jitter (ms), %s\n" % (name))

# Print some program initialization information.
print("\nThe time is: %s" % (startTimeStr))
print("Reading %s %i times and saving data to the file:\n - %s\n" % (name, numIterations, filePath))

# Prepare final variables for program execution.
intervalHandle = 0
ljm.startInterval(intervalHandle, rateUS)
numSkippedIntervals = 0

lastTick = ljm.getHostTick()
duration = 0

for i in range(numIterations):
    try:
        numSkippedIntervals = ljm.waitForNextInterval(intervalHandle)

        # Calculate the time since the last interval.
        curTick = ljm.getHostTick()
        duration = (curTick-lastTick)/1000

        # Get and format a timestamp.
        curTime = datetime.datetime.now()
        curTimeStr = curTime.strftime(timestampFormat)

        # Read AIN0.
        result = ljm.eReadName(handle, name)

        # Print the results.
        print("%s reading: %0.6f V, duration: %0.1f ms, skipped intervals: %i" % (name, result, duration, numSkippedIntervals))

        # Write the results to file.
        f.write("%s, %0.1f, %0.6f\n" % (curTimeStr, duration, result))

        lastTick = curTick
    except Exception:
        print(sys.exc_info()[1])
        break

print("\nFinished!")

# Get the final time.
appEndTime = datetime.datetime.now()
#endTimeStr = appEndTime.isoformat(timespec='milliseconds')
endTimeStr = appStartTime.strftime(timestampFormat)
print("The final time is: %s" % (endTimeStr))

# Close the file.
f.close()

# Close the interval and device handles.
ljm.cleanInterval(intervalHandle)
ljm.close(handle)
