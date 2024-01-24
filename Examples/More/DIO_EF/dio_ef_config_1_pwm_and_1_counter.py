"""
Enables a 10 kHz PWM output and high-speed counter, waits 1 second, and reads
the counter. If you jumper the counter to the PWM the value read from the
counter should be close to 10000.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    Multiple Value Functions(such as eWriteNames):
        https://labjack.com/support/software/api/ljm/function-reference/multiple-value-functions

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Digital I/O:
        https://labjack.com/support/datasheets/t-series/digital-io
    Extended DIO Features:
        https://labjack.com/support/datasheets/t-series/digital-io/extended-features
    PWM Out:
        https://labjack.com/support/datasheets/t-series/digital-io/extended-features/pwm-out
    High-Speed Counter:
        https://labjack.com/support/datasheets/t-series/digital-io/extended-features/high-speed-counter

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

# Configure the PWM output and counter.
if deviceType == ljm.constants.dtT8:
    # For the T8, use FIO7 (DIO7) for the PWM output.
    # Use FIO6 (DIO6) for the high speed counter.
    pwmDIO = 7
    counterDIO = 6

    # Clock0Frequency = 100MHz / 1 = 100MHz
    # PWMFrequency = 100MHz / 10000 = 10000
    # DutyCycle% = 100 * 5000 / 10000 = 50%
    clockDivisor = 1  # DIO_EF_CLOCK0_DIVISOR
    clockRollValue = 10000  # DIO_EF_CLOCK0_ROLL_VALUE
    pwmConfigA = 5000  # DIO0_EF_CONFIG_A
else:
    if deviceType == ljm.constants.dtT4:
        # For the T4, use FIO6 (DIO6) for the PWM output.
        # Use CIO2 (DIO18) for the high speed counter.
        pwmDIO = 6
        counterDIO = 18

        # Set FIO and EIO lines to digital I/O.
        ljm.eWriteNames(handle, 2,
                        ["DIO_INHIBIT", "DIO_ANALOG_ENABLE"],
                        [0xFBF, 0x000])
    else:
        # For the T7, use FIO0 (DIO0) for the PWM output.
        # Use CIO2 (DIO18) for the high speed counter.
        pwmDIO = 0
        counterDIO = 18

    # Clock0Frequency = 80MHz / 1 = 80MHz
    # PWMFrequency = 80MHz / 8000 = 10000
    # DutyCycle% = 100 * 4000 / 8000 = 50%
    clockDivisor = 1  # DIO_EF_CLOCK0_DIVISOR
    clockRollValue = 8000  # DIO_EF_CLOCK0_ROLL_VALUE
    pwmConfigA = 4000  # DIO0_EF_CONFIG_A

aNames = ["DIO_EF_CLOCK0_DIVISOR", "DIO_EF_CLOCK0_ROLL_VALUE",
          "DIO_EF_CLOCK0_ENABLE", "DIO%i_EF_ENABLE" % pwmDIO,
          "DIO%i_EF_INDEX" % pwmDIO, "DIO%i_EF_CONFIG_A" % pwmDIO,
          "DIO%i_EF_ENABLE" % pwmDIO, "DIO%i_EF_ENABLE" % counterDIO,
          "DIO%i_EF_INDEX" % counterDIO, "DIO%i_EF_ENABLE" % counterDIO]
aValues = [clockDivisor, clockRollValue,
           1, 0,
           0, pwmConfigA,
           1, 0,
           7, 1]
numFrames = len(aNames)
results = ljm.eWriteNames(handle, numFrames, aNames, aValues)

# Wait 1 second.
time.sleep(1.0)

# Read from the counter.
value = ljm.eReadName(handle, "DIO%i_EF_READ_A" %counterDIO)

print("\nCounter = %f" % (value))

# Turn off PWM output and counter
aNames = ["DIO_EF_CLOCK0_ENABLE", "DIO%i_EF_ENABLE" % pwmDIO,
          "DIO%i_EF_ENABLE" % counterDIO]
aValues = [0, 0, 0]
numFrames = len(aNames)
results = ljm.eWriteNames(handle, numFrames, aNames, aValues)

# Close handle
ljm.close(handle)
