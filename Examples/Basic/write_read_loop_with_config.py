"""
Performs an initial call to eWriteNames to write configuration values, and then
calls eWriteNames and eReadNames repeatedly in a loop.

For documentation on register names to use, see the T-series Datasheet or the
Modbus Map:

https://labjack.com/support/datasheets/t-series
https://labjack.com/support/software/examples/modbus/modbus-map

"""
import sys

from labjack import ljm


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
    loopAmount = "infinite"
    loopMessage = " Press Ctrl+C to stop."

# Open first found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
#handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
#handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
#handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

deviceType = info[0]

# Setup and call eWriteNames for AIN0 (all devices) and digital I/O (T4 only)
# configuration.
if deviceType == ljm.constants.dtT4:
    # LabJack T4 configuration

    # Set FIO5 (DIO5) and FIO6 (DIO6) lines to digital I/O.
    #     DIO_INHIBIT = 0xF9F, b111110011111.
    #                   Update only DIO5 and DIO6.
    #     DIO_ANALOG_ENABLE = 0x000, b000000000000.
    #                         Set DIO5 and DIO6 to digital I/O (b0).
    aNames = ["DIO_INHIBIT", "DIO_ANALOG_ENABLE"]
    aValues = [0xF9F, 0x000]
    numFrames = len(aNames)
    ljm.eWriteNames(handle, numFrames, aNames, aValues)

    # AIN0:
    #     The T4 only has single-ended analog inputs.
    #     The range of AIN0-AIN3 is +/-10 V.
    #     The range of AIN4-AIN11 is 0-2.5 V.
    #     Resolution index = 0 (default)
    #     Settling = 0 (auto)
    aNames = ["AIN0_RESOLUTION_INDEX", "AIN0_SETTLING_US"]
    aValues = [0, 0]
else:
    # LabJack T7 and other devices configuration

    # AINO:
    #     Negative Channel = 199 (Single-ended)
    #     Range = +/- 10 V
    #     Resolution index = 0 (default)
    #     Settling = 0 (auto)
    aNames = ["AIN0_NEGATIVE_CH", "AIN0_RANGE", "AIN0_RESOLUTION_INDEX",
              "AIN0_SETTLING_US"]
    aValues = [199, 10, 0, 0]
numFrames = len(aNames)
ljm.eWriteNames(handle, numFrames, aNames, aValues)

print("\nSet configuration:")
for i in range(numFrames):
    print("    %s : %f" % (aNames[i], aValues[i]))

print("\nStarting %s read loops.%s\n" % (str(loopAmount), loopMessage))
i = 0
dacVolt = 0.0
fioState = 0
intervalHandle = 1
ljm.startInterval(intervalHandle, 1000000)
while True:
    try:
        # Setup and call eWriteNames to write to DAC0, and FIO5 (T4) or
        # FIO1 (T7 and other devices).
        # DAC0 will cycle ~0.0 to ~5.0 volts in 1.0 volt increments.
        # FIO5/FIO1 will toggle output high (1) and low (0) states.
        if deviceType == ljm.constants.dtT4:
            aNames = ["DAC0", "FIO5"]
        else:
            aNames = ["DAC0", "FIO1"]
        dacVolt = i % 6.0  # 0-5
        fioState = i % 2  # 0 or 1
        aValues = [dacVolt, fioState]
        numFrames = len(aNames)
        ljm.eWriteNames(handle, numFrames, aNames, aValues)
        print("\neWriteNames : " +
              "".join(["%s = %f, " % (aNames[j], aValues[j]) for j in range(numFrames)]))

        # Setup and call eReadNames to read AIN0 and FIO6 (T4) for
        # FIO2 (T7 and other devices).
        if deviceType == ljm.constants.dtT4:
            aNames = ["AIN0", "FIO6"]
        else:
            aNames = ["AIN0", "FIO2"]
        numFrames = len(aNames)
        aValues = ljm.eReadNames(handle, numFrames, aNames)
        print("eReadNames  : " +
              "".join(["%s = %f, " % (aNames[j], aValues[j]) for j in range(numFrames)]))

        # Repeat every 1 second
        skippedIntervals = ljm.waitForNextInterval(intervalHandle)
        if skippedIntervals > 0:
            print("\nSkippedIntervals: %s" % skippedIntervals)

        i += 1
        if loopAmount is not "infinite":
            if i >= loopAmount:
                break
    except KeyboardInterrupt:
        break
    except Exception:
        import sys
        print(sys.exc_info()[1])
        break

# Close interval and device handles
ljm.cleanInterval(intervalHandle)
ljm.close(handle)
