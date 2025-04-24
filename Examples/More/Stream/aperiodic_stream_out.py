"""
Demonstrates usage of the aperiodic stream-out functions.

Streams out two alternating sine waves on DAC0. Values are generated before the
stream starts in this demonstration, but could be dynamically generated, read
from a file, etc., during the stream run time.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    LJM Single Value Functions (like eReadName, eReadAddress):
        https://labjack.com/support/software/api/ljm/function-reference/single-value-functions
    Stream Functions (eStreamStart, eStreamStop, initializeAperiodicStreamOut
    and writeAperiodicStreamOut):
        https://labjack.com/support/software/api/ljm/function-reference/stream-functions

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Stream Mode:
        https://labjack.com/support/datasheets/t-series/communication/stream-mode
    Analog Inputs:
        https://labjack.com/support/datasheets/t-series/ain
    Stream-Out:
        https://labjack.com/support/datasheets/t-series/communication/stream-mode/stream-out
    Digital I/O:
        https://labjack.com/support/datasheets/t-series/digital-io
    DAC:
        https://labjack.com/support/datasheets/t-series/dac

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
import math
import time

from labjack import ljm


def generateSineWave(amp, freq, phase, numSamples, sampleRate, dcOffset):
    """
    Generates a sine wave as a list of samples.

    Args:
        amp: The amplitude of the sine wave.
        freq: The frequency of the sine wave in Hz.
        phase: The phase of the sine wave in radians.
        numSamples: The number of samples to generate.
        sampleRate: The sample rate in Hz. This is the scan rate of
                    the stream mode.

    Returns:
        A list of floats representing the sine wave samples.

    """
    wave = []
    for i in range(numSamples):
        time = i / sampleRate
        sample = amp * math.sin(2 * math.pi * freq * time + phase) + dcOffset
        wave.append(sample)
    return wave


# Open the first found LabJack.
handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
#handle = ljm.openS("T8", "ANY", "ANY")  # T8 device, Any connection, Any identifier
#handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
#handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
#handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

# Display the currently opened device information.
info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Stream settings

# Scan rate in Hz.
scanRate = 10000
# Not streaming inputs so scansPerRead is not used. Needs to be a non-zero
# value for stream start.
scansPerRead = 1
# The LJM max. buffer size for the aperiodic stream-out function.
ljmBufferSize = scanRate * 20
# Using stream out index 0 (valid indexes are 0-3).
streamOutIndex = 0
# Stream-out 0 target is DAC0. Note that the register address needs to be used.
streamOutTarget = ljm.nameToAddress("DAC0")[0]
# Scan list will be STREAM_OUT0, whose target is DAC0. Note that the register
# address needs to be used.
scanList = [ljm.nameToAddress("STREAM_OUT%d" % streamOutIndex)[0]]

# Generate our waveforms.
waveforms = [0]*2
waveforms[0] = generateSineWave(amp=1, freq=500, phase=0, numSamples=1000, sampleRate=scanRate, dcOffset=2)
waveforms[1] = generateSineWave(amp=2, freq=1000, phase=0, numSamples=1000, sampleRate=scanRate, dcOffset=2)
waveformCount = 0  # Keeps track of which waveform to update with.
waveformCountMax = len(waveforms)  # The total number of waveforms.

# Try to stop any previously ran stream.
try:
    ljm.eStreamStop(handle)
except:
    pass

# Initialize aperiodic stream out.
ljm.initializeAperiodicStreamOut(handle, streamOutIndex, streamOutTarget, scanRate)

# Write some data to the buffer before the stream starts.
ljm.writeAperiodicStreamOut(handle, streamOutIndex, len(waveforms[0]), waveforms[0])
ljm.writeAperiodicStreamOut(handle, streamOutIndex, len(waveforms[1]), waveforms[1])

# Configure and start stream mode with stream-out channel.
scanRate = ljm.eStreamStart(handle, scansPerRead, len(scanList), scanList, scanRate)

# Update the waveform for 20 seconds.

# How long to run our stream-out in the loop.
runTimeMax = 20
# Loop rate in Hz. When streaming in data also, this is the
# scan rate / scans per read.
loopRate = 10
# Used to determine when to load new stream-out data, in seconds.
# Users may need to adjust.
loadThreshhold = 1.0 / loopRate
# The start time to keep track how long our loop has run for.
startTime = time.time()
# A user set handle for the interval timer.
intervalHandle = 1
# Interval timer to delay loop, in microseconds. Based on loopRate.
ljm.startInterval(intervalHandle, int(1000000 // loopRate))

while (time.time() - startTime) < runTimeMax:
    # Get the LJM buffer status. No additional data written to stream out buffer.
    ljmBufferStatus = ljm.writeAperiodicStreamOut(handle, streamOutIndex, 0, [])
    print("\nLJM Buffer Status = %d" % ljmBufferStatus)

    # Number of seconds until LJM buffer is empty.
    secondsUntilEmpty = (200000 - ljmBufferStatus) / scanRate
    if secondsUntilEmpty < loadThreshhold:
        # Add new data to stream out when above threshold.
        ljmBufferStatus = ljm.writeAperiodicStreamOut(handle, streamOutIndex, len(waveforms[waveformCount]), waveforms[waveformCount])
        print("Wrote %d samples from waveform %d to stream-out" % (len(waveforms[waveformCount]), waveformCount))

        # Figure out which waveform to update with next.
        waveformCount += 1
        if waveformCount >= waveformCountMax:
            waveformCount = 0

    # Wait until next loopRate interval. Not needed when reading stream inputs.
    skippedIntervals = ljm.waitForNextInterval(intervalHandle)

# Clean up interval memory.
ljm.cleanInterval(intervalHandle)

# Stop stream mode.
ljm.eStreamStop(handle)
