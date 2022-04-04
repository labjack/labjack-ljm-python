'''
Shows how to stream with the T7 or T8 in external clock stream mode.
Note: Similar to stream_callback.py, which uses a callback to read from stream.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    Utility Functions (such as NamesToAddresses):
        https://labjack.com/support/software/api/ljm/function-reference/utility
    Stream Functions:
        https://labjack.com/support/software/api/ljm/function-reference/stream-functions
    Constants:
        https://labjack.com/support/software/api/ljm/constants
    Library Configuration Functions:
        https://labjack.com/support/software/api/ljm/function-reference/library-configuration-functions

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Stream Mode:
        https://labjack.com/support/datasheets/t-series/communication/stream-mode
    Analog Inputs:
        https://labjack.com/support/datasheets/t-series/ain
    Stream-Out:
        https://labjack.com/support/datasheets/t-series/communication/stream-mode/stream-out/stream-out-description
    Digital I/O:
        https://labjack.com/support/datasheets/t-series/digital-io
    Pulse Out:
        https://labjack.com/support/datasheets/t-series/digital-io/extended-features/pulse-out
    Stream Mode (externally clocked):
        https://labjack.com/support/datasheets/t-series/communication/stream-mode#externally-clocked
    Hardware Overview(Device Information Registers):
        https://labjack.com/support/datasheets/t-series/hardware-overview
'''
import sys
from datetime import datetime
import ljm_stream_util
from labjack import ljm

def HardcodedConfigureStream(handle):

    STREAM_TRIGGER_INDEX = 0
    STREAM_RESOLUTION_INDEX = 0
    STREAM_SETTLING_US = 0
    AIN_ALL_RANGE = 0
    AIN_ALL_NEGATIVE_CH = ljm.constants.GND

    print("Writing configurations:")

    if STREAM_TRIGGER_INDEX == 0:
        print("    Ensuring triggered stream is disabled:")

    print("    Setting STREAM_TRIGGER_INDEX to %d" % STREAM_TRIGGER_INDEX)
    ljm.eWriteName(handle, "STREAM_TRIGGER_INDEX", STREAM_TRIGGER_INDEX)

    # Configure the analog inputs' negative channel, range, settling time and
    # resolution.
    # Note: when streaming, negative channels and ranges can be configured for
    # individual analog inputs, but the stream has only one settling time and
    # resolution. The settling time and negative channel configurations do not
    # do anything on the T8 due to the isolated and simultaneously sampled AIN.
    print("    Setting STREAM_RESOLUTION_INDEX to %d" %
        STREAM_RESOLUTION_INDEX)
    ljm.eWriteName(handle, "STREAM_RESOLUTION_INDEX", STREAM_RESOLUTION_INDEX)

    print("    Setting STREAM_SETTLING_US to %f" % STREAM_SETTLING_US)
    ljm.eWriteName(handle, "STREAM_SETTLING_US", STREAM_SETTLING_US)

    print("    Setting AIN_ALL_RANGE to %f" % AIN_ALL_RANGE)
    ljm.eWriteName(handle, "AIN_ALL_RANGE", AIN_ALL_RANGE)

    print("    Setting AIN_ALL_NEGATIVE_CH to %s" %
        "LJM_GND" if AIN_ALL_NEGATIVE_CH == ljm.constants.GND
        else AIN_ALL_NEGATIVE_CH)

    print("\n")
    ljm.eWriteName(handle, "AIN_ALL_NEGATIVE_CH", AIN_ALL_NEGATIVE_CH)


def EnableFIO0PulseOut(handle, pulseRate, numPulses):
    # Set FIO0 to do a 50% duty cycle
    # https://labjack.com/support/datasheets/t-series/digital-io/extended-features/pulse-out

    rollValue = 10000000/pulseRate

    print("\nEnabling %d pulses on FIO0 at a %d Hz pulse rate\n" % (numPulses, pulseRate))

    ljm.eWriteName(handle, "DIO0_EF_ENABLE", 0)
    ljm.eWriteName(handle, "DIO_EF_CLOCK0_DIVISOR", 8)
    ljm.eWriteName(handle, "DIO_EF_CLOCK0_ROLL_VALUE", int(rollValue))
    ljm.eWriteName(handle, "DIO_EF_CLOCK0_ENABLE", 1)
    ljm.eWriteName(handle, "DIO0_EF_INDEX", 2)
    ljm.eWriteName(handle, "DIO0_EF_OPTIONS", 0)
    ljm.eWriteName(handle, "DIO0", 0)
    ljm.eWriteName(handle, "DIO0_EF_CONFIG_A", int(rollValue/2))
    ljm.eWriteName(handle, "DIO0_EF_CONFIG_B", 0)
    ljm.eWriteName(handle, "DIO0_EF_CONFIG_C", int(numPulses))
    ljm.eWriteName(handle, "DIO0_EF_ENABLE", 1)



def StreamReturnAllOrNone(handle):

    FIO0PulseOut = 1
    maxRequests = 10

    # Variables for LJM_eStreamStart
    scanRate = 1000
    scansPerRead = scanRate/2

    # Configure LJM for unpredictable stream timing
    ljm.writeLibraryConfigS(ljm.constants.STREAM_SCANS_RETURN,
        ljm.constants.STREAM_SCANS_RETURN_ALL_OR_NONE)
    ljm.writeLibraryConfigS(ljm.constants.STREAM_RECEIVE_TIMEOUT_MODE,
        ljm.constants.STREAM_RECEIVE_TIMEOUT_MODE_MANUAL)
    ljm.writeLibraryConfigS(ljm.constants.STREAM_RECEIVE_TIMEOUT_MS, 100)

    aNames = ["AIN0","AIN1","AIN2","AIN3"]
    numAddresses = len(aNames)
    aScanList = ljm.namesToAddresses(numAddresses, aNames)[0]

    HardcodedConfigureStream(handle)

    print("Starting externally clocked stream...")
    # Set external clock source on CIO3
    ljm.eWriteName(handle, "STREAM_CLOCK_SOURCE", 2)
    ljm.eWriteName(handle, "STREAM_EXTERNAL_CLOCK_DIVISOR", 1)

    if FIO0PulseOut == 1:
        EnableFIO0PulseOut(handle, scanRate, scanRate*maxRequests + 5000)

    ljm.eStreamStart(handle, int(scansPerRead), numAddresses, aScanList, scanRate)
    i = 1
    ljmScanBacklog = 0
    totScans = 0
    totSkip = 0

    start = datetime.now()
    while i <= maxRequests:
        ljm_stream_util.variableStreamSleep(scansPerRead, scanRate, ljmScanBacklog)

        try:
            ret = ljm.eStreamRead(handle)

            aData = ret[0]
            ljmScanBacklog = ret[2]
            scans = len(aData) / numAddresses
            totScans += scans

            # Count the skipped samples which are indicated by -9999 values. Missed
            # samples occur after a device's stream buffer overflows and are
            # reported after auto-recover mode ends.
            curSkip = aData.count(-9999.0)
            totSkip += curSkip

            print("\neStreamRead %i" % i)
            ainStr = ""
            for j in range(0, numAddresses):
                ainStr += "%s = %0.5f, " % (aNames[j], aData[j])
            print("  1st scan out of %i: %s" % (scans, ainStr))
            print("  Scans Skipped = %0.0f, Scan Backlogs: Device = %i, LJM = "
                  "%i" % (curSkip/numAddresses, ret[1], ljmScanBacklog))
            i += 1
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



if __name__ == "__main__":

    try:
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

        if deviceType == ljm.constants.dtT4:
            print("The T4 does not support externally clocked stream.")
            print("Exiting now.")
            exit(1)

        # Disable stream if enabled
        if ljm.eReadName(handle, "STREAM_ENABLE") == 1:
            ljm.eWriteName(handle, "STREAM_ENABLE", 0)

        StreamReturnAllOrNone(handle)

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