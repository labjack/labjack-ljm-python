"""
Enables a 10 kHz PWM output on FIO0, enables a high-speed counter on DIO18/CIO2,
waits 1 second and reads the counter. Jumper FIO0 to CIO2 and the read value
should return around 10000.

DIO extended features, PWM output and high-speed counter documented here:

https://labjack.com/support/datasheets/t7/digital-io/extended-features
https://labjack.com/support/datasheets/t7/digital-io/extended-features/pwm-out
https://labjack.com/support/datasheets/t7/digital-io/extended-features/high-speed-counter

"""

from labjack import ljm
import time

# Open first found LabJack.
handle = ljm.openS("ANY", "ANY", "ANY")
#handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Configure the PWM output and counter.
aNames = ["DIO_EF_CLOCK0_DIVISOR", "DIO_EF_CLOCK0_ROLL_VALUE",
          "DIO_EF_CLOCK0_ENABLE", "DIO0_EF_INDEX",
          "DIO0_EF_CONFIG_A", "DIO0_EF_ENABLE",
          "DIO18_EF_INDEX", "DIO18_EF_ENABLE"]
aValues = [1, 8000,
           1, 0,
           2000, 1,
           7, 1]
numFrames = len(aNames)
results = ljm.eWriteNames(handle, numFrames, aNames, aValues)

# Wait 1 second.
time.sleep(1.0)

# Read from the counter.
value = ljm.eReadName(handle, "DIO18_EF_READ_A")

print("\nCounter = %f" % (value))

# Turn off PWM output and counter
aNames = ["DIO_EF_CLOCK0_ENABLE", "DIO0_EF_ENABLE"]
aValues = [0, 0]
numFrames = len(aNames)
results = ljm.eWriteNames(handle, numFrames, aNames, aValues)

# Close handle
ljm.close(handle)
