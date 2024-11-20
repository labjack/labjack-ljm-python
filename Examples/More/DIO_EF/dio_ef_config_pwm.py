"""
Enables a 10 kHz PWM output for 10 seconds.

To configure PWM to user desired frequency and duty cycle, modify the
"desiredFrequency" and "desiredDutyCycle" variables.

For more information on the PWM DIO_EF mode see section 13.2.2 of the T-Series
Datasheet:
https://support.labjack.com/docs/13-2-2-pwm-out-t-series-datasheet

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


#------------- USER INPUT VALUES -------------
desiredFrequency = 10000  # Set this value to your desired PWM Frequency Hz. Defualt 10000 Hz
desiredDutyCycle = 50     # Set this value to your desired PWM Duty Cycle percentage. Default 50%
# ---------------------------------------------


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


# --- Configure Clock and PWM ---
pwmDIO = 0  # DIO Pin that will generate the PWM signal, set based on device type below.
coreFrequency = 0  # Device Specific Core Clock Frequency, used to calculate Clock Roll Value.
clockDivisor = 1  # Clock Divisor to use in configuration.

# --- Configure device specific values ---
# Selecting a specific DIO# Pin is necessary for each T-Series Device, only specific DIO# pins can output a PWM signal.
# For detailed T-Series Device DIO_EF pin mapping tables see section 13.2 of the T-Series Datasheet:
# https://support.labjack.com/docs/13-2-dio-extended-features-t-series-datasheet
if deviceType == ljm.constants.dtT4:
    # For the T4, use FIO6 (DIO6) for the PWM output. T4 Core Clock Speed is 80 MHz.
    pwmDIO = 6
    coreFrequency = 80000000
elif deviceType == ljm.constants.dtT7:
    # For the T7, use FIO2 (DIO2) for the PWM output. T7 Core Clock Speed is 80 MHz.
    pwmDIO = 2
    coreFrequency = 80000000
elif deviceType == ljm.constants.dtT8:
    # For the T8, use FIO2 (DIO2) for the PWM output. T8 Core Clock Speed is 100 MHz.
    pwmDIO = 2
    coreFrequency = 100000000
else:
    ljm.close(handle)
    raise ValueError("Unknown LabJack device type %s. " % deviceType)

# --- How to Configure a Clock and PWM Signal? ---
# See Datasheet reference for DIO_EF Clocks:
# https://support.labjack.com/docs/13-2-1-ef-clock-source-t-series-datasheet
#
# To configure a DIO_EF PWM out signal, you first need to configure the clock used by the DIO_EF mode.
#
# --- Registers used for configuring Clocks ---
# "DIO_FE_CLOCK#_DIVISOR":    Divides the core clock. Valid options: 1, 2, 4, 8, 16, 32, 64, 256.
# "DIO_EF_CLOCK#_ROLL_VALUE": The clock count will increment continuously and then start over at zero as it reaches the roll value.
# "DIO_EF_CLOCK#_ENABLE":     Enables/Disables the Clock.
#
# --- Registers used for configuring PWM ---
# "DIO#_EF_INDEX":            Sets desired DIO_EF feature, DIO_EF PWM mode is index 0.
# "DIO#_EF_CLOCK_SOURCE":     (Formerly DIO#_EF_OPTIONS). Specify which clock source to use.
# "DIO#_EF_CONFIG_A":         When the clocks count matches this value, the line will transition from high to low.
# "DIO#_EF_ENABLE":           Enables/Disables the DIO_EF mode.
#
# To configure a DIO_EF clock to any desired frequency, you need to calculate the Clock Tick Rate and then the Clock Roll Value.
# Clock Tick Rate = Core Frequency / DIO_EF_CLOCK#_DIVISOR
# Clock Roll Value = Clock Tick Rate / Desired Frequency
#
# In general, a slower Clock#Frequency will increase the maximum measurable period,
# and a faster Clock#Frequency will increase measurement resolution.
#
# For more information on DIO_EF Clocks see section 13.2.1 - EF Clock Source of the T-Series Datasheet:
# https://support.labjack.com/docs/13-2-1-ef-clock-source-t-series-datasheet
#
# For a more detailed walkthrough see Configuring a PWM Output:
# https://support.labjack.com/docs/configuring-a-pwm-output

# Calculate Clock Values
clockDivisor = 1
clockTickRate = coreFrequency / clockDivisor
clockRollValue = clockTickRate / desiredFrequency  # clockRollValue should be written to "DIO_EF_CLOCK0_ROLL_VALUE"

# Below is a single equation which calculates the same value as the above equations
#clockRollValue = coreFrequency / clockDivisor / desiredFrequency


# --- Calculate PWM Values ---
# Calculate the clock tick value where the line will transition from high to low based on user defined duty cycle percentage, rounded to the nearest integer.
pwmConfigA = int(clockRollValue * (desiredDutyCycle / 100.0))

# What the PWM signal will look like based on Clock0 Count for a 50% Duty Cycle.
# PWM will go high when Clock Count = 0, and then go low halfway to the Clock Roll Value thus a 50% duty cycle.
#  __________            __________
# |          |          |          |          |
# |          |__________|          |__________|
# 0        Roll/2      Roll      Roll/2      Roll
# 0          50%       100%       50%        100%

# --- Configure and write values to connected device ---
# Configure Clock Registers, use 32-bit Clock0 for this example.
ljm.eWriteName(handle, "DIO_EF_CLOCK0_DIVISOR", clockDivisor)     # Set Clock Divisor.
ljm.eWriteName(handle, "DIO_EF_CLOCK0_ROLL_VALUE", clockRollValue)  # Set calculated Clock Roll Value.

# Configure PWM Registers
ljm.eWriteName(handle, "DIO%d_EF_INDEX" % pwmDIO, 0)              # Set DIO#_EF_INDEX to 0 - PWM Out.
ljm.eWriteName(handle, "DIO%d_EF_CLOCK_SOURCE" % pwmDIO, 0)       # Set DIO#_EF to use clock 0. Formerly DIO#_EF_OPTIONS, you may need to switch to this name on older LJM versions.
ljm.eWriteName(handle, "DIO%d_EF_CONFIG_A" % pwmDIO, pwmConfigA)  # Set DIO#_EF_CONFIG_A to the calculated value.
ljm.eWriteName(handle, "DIO%d_EF_ENABLE" % pwmDIO, 1)             # Enable the DIO#_EF Mode, PWM signal will not start until DIO_EF and CLOCK are enabled.

ljm.eWriteName(handle, "DIO_EF_CLOCK0_ENABLE", 1)                 # Enable Clock0, this will start the PWM signal.


print("A PWM Signal at %.1f Hz with a duty cycle of %.1f %% is now being output on DIO%d for 10 seconds." %
      (desiredFrequency, desiredDutyCycle, pwmDIO))

time.sleep(10.0)  # Sleep for 10 Seconds = 10000 ms, remove this line to allow PWM to run until stopped.

# Turn off Clock and PWM output.
aNames = ["DIO_EF_CLOCK0_ENABLE",
          "DIO%d_EF_ENABLE" % pwmDIO]
aValues = [0,
           0]
numFrames = len(aNames)
ljm.eWriteNames(handle, numFrames, aNames, aValues)


# Close handle
ljm.close(handle)
