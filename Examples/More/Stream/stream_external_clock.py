'''
Demonstrates how to stream with the T7 or T8 in external clock stream mode.
Connect CIO3 (T7) or FIO2 (T8) to FIO3 to use Pulse Out for the stream clock.

Note: The T4 is not supported in this example.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    NamesToAddresses:
        https://labjack.com/support/software/api/ljm/function-reference/utility/ljmnamestoaddresses
    eWriteName:
        https://labjack.com/support/software/api/ljm/function-reference/ljmewritename
    eWriteNames:
        https://labjack.com/support/software/api/ljm/function-reference/ljmewritenames
    Stream Functions (such as eStreamStart, eStreamRead and eStreamStop):
        https://labjack.com/support/software/api/ljm/function-reference/stream-functions
    eStreamStart (for eStreamStart and externally clock stream in LJM)
        https://labjack.com/support/ljm/users-guide/function-reference/ljmestreamstart
    Library Configuration Functions (such as WriteLibraryConfigS and stream parameters):
        https://labjack.com/support/software/api/ljm/function-reference/library-configuration-functions

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Stream Mode:
        https://labjack.com/support/datasheets/t-series/communication/stream-mode
    Special Stream Modes (such as externally clocked):
        https://support.labjack.com/docs/3-2-2-special-stream-modes-t-series-datasheet
    Analog Inputs:
        https://labjack.com/support/datasheets/t-series/ain
    Digital I/O:
        https://labjack.com/support/datasheets/t-series/digital-io
    Hardware Overview (such as register CORE_TIMER):
        https://labjack.com/support/datasheets/t-series/hardware-overview
    Pulse Out:
        https://labjack.com/support/datasheets/t-series/digital-io/extended-features/pulse-out

Note:
    Our Python interfaces throw exceptions when there are any issues with
    device communications that need addressed. Many of our examples will
    terminate immediately when an exception is thrown. The onus is on the API
    user to address the cause of any exceptions thrown, and add exception
    handling when appropriate. We create our own exception classes that are
    derived from the built-in Python Exception class and can be caught as such.
    For more information, see the implementation in our source code and the
    Python standard documentation.
'''
import sys
from datetime import datetime
from time import sleep

from labjack import ljm


def variableStreamSleep(scansPerRead, scanRate, LJMScanBacklog):
    """Sleeps for approximately the expected amount of time until the next scan
    is ready to be read.

    @para scansPerRead: The number of scans returned by a eStreamRead call.
    @type scansPerRead: int
    @para scanRate: The stream scan rate.
    @type scanRate: numerical
    @para LJMScanBacklog: The number of backlogged scans in the LJM buffer.
    @type LJMScanBacklog: int
    """
    DECREASE_TOTAL = 0.9
    sleepFactor = 0.0
    portionScansReady = float(LJMScanBacklog) / scansPerRead
    if portionScansReady <= DECREASE_TOTAL:
        sleepFactor = (1 - portionScansReady) * DECREASE_TOTAL
    sleepTime = sleepFactor * scansPerRead / float(scanRate)
    sleep(sleepTime)


if __name__ == "__main__":
    try:
        # Open first found LabJack
        handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
        #handle = ljm.openS("T8", "ANY", "ANY")  # T8 device, Any connection, Any identifier
        #handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
        #handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

        info = ljm.getHandleInfo(handle)
        print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
              "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
              (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

        deviceType = info[0]

        if deviceType == ljm.constants.dtT4:
            print("The T4 does not support externally clocked stream.")
            print("Exiting now.")
            exit(1)

        # Configure negative channels and stream settling.
        # Not applicable to the T8.
        if deviceType == ljm.constants.dtT7:
            # All negative channels are single-ended.
            # Stream settling is 0 (default).
            aNames = ["AIN_ALL_NEGATIVE_CH", "STREAM_SETTLING_US"]
            aValues = [ljm.constants.GND, 0]
            numFrames = len(aNames)
            ljm.eWriteNames(handle, numFrames, aNames, aValues)

        # Ensure triggered stream is disabled.
        # AIN ranges are set to ±10V (T7) or ±11V (T8).
        # Stream resolution index is 0 (default).
        aNames = ["STREAM_TRIGGER_INDEX", "AIN_ALL_RANGE",
                  "STREAM_RESOLUTION_INDEX"]
        aValues = [0, 10.0,
                   0]
        numFrames = len(aNames)
        ljm.eWriteNames(handle, numFrames, aNames, aValues)

        # Stream Configuration
        FIO3_CLOCK = True  # Use Pulse Out on FIO3 for the stream clock
        NUM_LOOP_ITERATIONS = 10
        scanRate = 1000  # Scans per second
        scansPerRead = scanRate/2  # Number of scans returned by eStreamRead call
        aScanListNames = ["AIN0", "FIO_STATE", "CORE_TIMER", "STREAM_DATA_CAPTURE_16"]  # Scan list names to stream.
        numAddresses = len(aScanListNames)
        aScanList = ljm.namesToAddresses(numAddresses, aScanListNames)[0]  # Scan list addresses to stream. eStreamStart uses Modbus addresses.

        # Configure LJM for unpredictable stream timing.
        ljm.writeLibraryConfigS(ljm.constants.STREAM_SCANS_RETURN,
            ljm.constants.STREAM_SCANS_RETURN_ALL_OR_NONE)
        ljm.writeLibraryConfigS(ljm.constants.STREAM_RECEIVE_TIMEOUT_MODE,
            ljm.constants.STREAM_RECEIVE_TIMEOUT_MODE_MANUAL)
        ljm.writeLibraryConfigS(ljm.constants.STREAM_RECEIVE_TIMEOUT_MS, 100)

        # Configure stream clock source to external clock source on
        # CIO3 for the T7, or FIO2 for the T8.
        print("\nSetting up externally clocked stream.\n")
        ljm.eWriteName(handle, "STREAM_CLOCK_SOURCE", 2)
        ljm.eWriteName(handle, "STREAM_EXTERNAL_CLOCK_DIVISOR", 1)

        if FIO3_CLOCK == True:
            # Enable Pulse Out with frequency of 1 kHz and 50% duty
            # cycle on FIO3.
            pulseRate = scanRate
            numPulses = scanRate*NUM_LOOP_ITERATIONS + 5000

            # Set the clock divisor so that the clock frequency is 10 MHz.
            if deviceType == ljm.constants.dtT8:
                # ClockFrequency = 100 MHz / 4 = 25 MHz
                # PulseOutFrequency = 25 MHz / 25 KHz = 1 KHz
                clockDivisor = 4
                rollValue = 25000
            else:
                # ClockFrequency = 80 MHz / 8 = 10 MHz
                # PulseOutFrequency = 10 MHz / 10 KHz = 1 KHz
                clockDivisor = 8
                rollValue = 10000

            # DutyCycle% = 100 * CONFIG_A / RollValue
            # CONFIG_A = DutyCycle% / 100 * RollValue
            dutyCyclePercent = 50
            dutyCycleValue = dutyCyclePercent / 100 * rollValue

            print("Enabling %d pulses on FIO3 at a %d Hz pulse rate.\n" % (numPulses, pulseRate))

            ljm.eWriteName(handle, "DIO3_EF_ENABLE", 0)
            ljm.eWriteName(handle, "DIO3", 0)
            ljm.eWriteName(handle, "DIO_EF_CLOCK0_DIVISOR", clockDivisor)
            ljm.eWriteName(handle, "DIO_EF_CLOCK0_ROLL_VALUE", rollValue)
            ljm.eWriteName(handle, "DIO_EF_CLOCK0_ENABLE", 1)
            ljm.eWriteName(handle, "DIO3_EF_INDEX", 2)
            ljm.eWriteName(handle, "DIO3_EF_CLOCK_SOURCE", 0)
            ljm.eWriteName(handle, "DIO3_EF_CONFIG_A", dutyCycleValue)
            ljm.eWriteName(handle, "DIO3_EF_CONFIG_B", 0)
            ljm.eWriteName(handle, "DIO3_EF_CONFIG_C", numPulses)
            ljm.eWriteName(handle, "DIO3_EF_ENABLE", 1)

        # Configure and start stream
        scanRate = ljm.eStreamStart(handle, int(scansPerRead), numAddresses, aScanList, scanRate)
        ljmScanBacklog = 0
        deviceScanBacklog = 0
        totScans = 0
        totSkip = 0

        start = datetime.now()
        i = 0
        while i < NUM_LOOP_ITERATIONS:
            try:
                variableStreamSleep(scansPerRead, scanRate, ljmScanBacklog)

                ret = ljm.eStreamRead(handle)

                aData = ret[0]
                deviceScanBacklog = ret[1]
                ljmScanBacklog = ret[2]
                scans = len(aData) / numAddresses
                totScans += scans

                # Count the skipped samples which are indicated by -9999 values.
                # Missed samples occur after a device's stream buffer overflows
                # and are reported after auto-recover mode ends.
                curSkip = aData.count(-9999.0)
                totSkip += curSkip
                i += 1

                print("\neStreamRead %i" % i)

                # Parse out first scan of samples to display.
                # CORE_TIMER and STREAM_DATA_CAPTURE_16 samples
                # are combined for the full 32-bit CORE_TIMER value.
                scanStr = ""
                coreTimer32bits = 0
                for j in range(numAddresses):
                    if j == 2:
                        # Sample 2 = CORE_TIMER
                        # CORE_TIMER is the lower 16-bits of the full
                        # 32-bit CORE_TIMER value.
                        coreTimer32bits = aData[j]
                    elif j == 3:
                        # Sample 3 = STREAM_DATA_CAPTURE_16
                        # STREAM_DATA_CAPTURE_16 is the upper 16-bits of the
                        # full 32-bit CORE_TIMER value.
                        coreTimer32bits += int(aData[j]) << 16
                        scanStr += "CORE_TIMER and STREAM_DATA_CAPTURE_16 = %d" % (coreTimer32bits)
                    else:
                        # Sample 0 = AIN0
                        # Sample 1 = FIO_STATE
                        scanStr += "%s = %0.5f, " % (aScanListNames[j], aData[j])

                print("  1st scan out of %i: %s" % (scans, scanStr))
                print("  Scans Skipped = %0.0f, Scan Backlogs: Device = %i, "
                    "LJM = %i" % (curSkip/numAddresses, deviceScanBacklog, ljmScanBacklog))
            except ljm.LJMError as err:
                if err.errorCode == ljm.errorcodes.NO_SCANS_RETURNED:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    continue
                else:
                    raise err
        end = datetime.now()

        print("\nTotal scans = %i" % (totScans))
        tt = (end - start).seconds + float((end - start).microseconds) / 1000000
        print("Time taken = %f seconds" % (tt))
        print("LJM Scan Rate = %f scans/second" % (scanRate))
        print("Timed Scan Rate = %f scans/second" % (totScans / tt))
        print("Timed Sample Rate = %f samples/second" % (totScans * numAddresses / tt))
        print("Skipped scans = %0.0f" % (totSkip / numAddresses))
    except ljm.LJMError:
        ljme = sys.exc_info()[1]
        print(ljme)
    except Exception:
        e = sys.exc_info()[1]
        print(e)

    try:
        print("\nStop Stream")
        ljm.eStreamStop(handle)
    except ljm.LJMError:
        ljme = sys.exc_info()[1]
        print(ljme)
    except Exception:
        e = sys.exc_info()[1]
        print(e)

    # Close handle
    ljm.close(handle)
