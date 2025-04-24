"""
Enables an Interrupt Counter measurement to rising edges and a 10 Hz square
wave on DAC1. To measure the rising edges on DAC1, connect a jumper between
DAC1 and FIO0 on T7/T8 or FIO4 on T4.

The Interrupt Counter counts the rising edge of pulses on the associated IO
line. This interrupt-based digital I/O extended feature (DIO-EF) is not purely
implemented in hardware, but rather firmware must service each edge.

This example will read the DAC1 rising edge count at 1 second intervals 5
times. Then the count will be read and reset, and after 1 second, the count is
read again.

For more information on the Interrupt Counter DIO_EF mode see section 13.2.9 of
the T-Series Datasheet.
https://support.labjack.com/docs/13-2-9-interrupt-counter-t-series-datasheet

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
import time

from labjack import ljm


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


# --- Interrupt Counter ---
counterDIO = 0  # DIO Pin that will measure the signal, T7/T8 use FIO0, T4 use FIO4.


# Selecting a specific DIO# Pin is necessary for each T-Series Device, only specific DIO# pins can do an Interrupt Counter measurement.
# For detailed T-Series Device DIO_EF pin mapping tables see section 13.2 of the T-Series Datasheet:
# https://support.labjack.com/docs/13-2-dio-extended-features-t-series-datasheet
if deviceType == ljm.constants.dtT4:
    # For the T4, use FIO4/DIO4 for the Interrupt Counter measurement.
    counterDIO = 4

# --- How to Configure Interrupt Counter Measurment ---
# See Datasheet reference for DIO_EF Interrupt Counter:
# https://support.labjack.com/docs/13-2-9-interrupt-counter-t-series-datasheet
#
# -- Registers used for configuring DAC1 Frequency Out ---
# "DAC1_FREQUENCY_OUT_ENABLE": 0 = off, 1 = output 10 Hz signal on DAC1. The signal will be a square wave with peaks of 0 and 3.3V.
#
# --- Registers used for configuring Interrupt Counter ---
# "DIO#_EF_INDEX":            Sets desired DIO_EF feature, Interrupt Counter is DIO_EF Index 8.
# "DIO#_EF_ENABLE":           Enables/Disables the DIO_EF mode.
#
# Interrupt Counter counts the rising edge of pulses on the associated IO line.
# This interrupt-based digital I/O extended feature (DIO-EF) is not purely implemented in hardware, but rather firmware must service each edge.
#
# For a more detailed walkthrough see Configuring and Reading a Counter:
# https://support.labjack.com/docs/configuring-reading-a-counter
#
# For a more accurate measurement for counting Rising edges, use the hardware clocked High-Speed Counter mode.
# See the docs for High-Speed Counter here:
# https://support.labjack.com/docs/13-2-8-high-speed-counter-t-series-datasheet


# Configure Interrupt Counter Registers
ljm.eWriteName(handle, "DIO%d_EF_INDEX" % counterDIO,  8)  # Set DIO#_EF_INDEX to 8 for Interrupt Counter.
ljm.eWriteName(handle, "DAC1_FREQUENCY_OUT_ENABLE",  1)    # Enable 10 Hz square wave on DAC1.
ljm.eWriteName(handle, "DIO%d_EF_ENABLE" % counterDIO, 1)  # Enable the DIO#_EF Mode.

print("\n--- Outputting a 10 Hz signal on DAC1, measuring signal on FIO%d ---\n" % counterDIO)

# --- How to read the measured count of rising edges? ---
# To read the count of Rising Edges, use the register below.
# DIO#_EF_READ_A: Returns the current Count.
#
# To read and reset the count:
# DIO#_EF_READ_A_AND_RESET: Reads the current count then clears the counter.
#
# Note that there is a brief period of time between reading and clearing during which edges can be missed.
# During normal operation this time period is 10-30 microseconds.
# If missed edges at this point can not be tolerated then reset should not be used.

# If measuring at 1 second intervals, you should expect to see ~10 rising edges per second on the 10 Hz DAC1_FREQUENCY_OUT signal.

numRisingEdges = 0
numRisingEdgesBeforeReset = 0
numRisingEdgesAfterReset  = 0

# Read all of the measured values.
for i in range(5):
    time.sleep(1.0)  # Sleep for 1 Second
    numRisingEdges = ljm.eReadName(handle, "DIO%d_EF_READ_A" % counterDIO)

    print("DIO_EF Measured Values - Rising Edges: %.1f" % numRisingEdges)

print("\n--- Reading and Resetting the count of DIO%d ---\n" % counterDIO)

numRisingEdgesBeforeReset = ljm.eReadName(handle, "DIO%d_EF_READ_A_AND_RESET" % counterDIO)
time.sleep(1.0)  # Sleep for 1 Second
numRisingEdgesAfterReset = ljm.eReadName(handle, "DIO%d_EF_READ_A_AND_RESET" % counterDIO)

print("DIO_EF Edges Before Read and Reset: %.1f" % numRisingEdgesBeforeReset)
print("DIO_EF Edges After Read and Reset + 1 sec sleep: %.1f" % numRisingEdgesAfterReset)


# Disable Counter and DAC1 Frequency Out.
aNames = ["DIO%d_EF_ENABLE" % counterDIO,
          "DAC1_FREQUENCY_OUT_ENABLE"]
aValues = [0,
           0,
           0]
numFrames = len(aNames)
print("\n--- Disabling Interrupt Counter and DAC1_FREQUENCY_OUT ---")
ljm.eWriteNames(handle, numFrames, aNames, aValues)


# Close handle
ljm.close(handle)
