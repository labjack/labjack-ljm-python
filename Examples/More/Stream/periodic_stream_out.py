"""
Demonstrates usage of the periodic stream-out functions.

Streams out arbitrary values. These arbitrary values act on DAC0 to cyclically
increase the voltage from 0 to 2.5.

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
    Stream Functions (eStreamRead, eStreamStart, etc.):
        https://labjack.com/support/software/api/ljm/function-reference/stream-functions

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Stream Mode:
        https://labjack.com/support/datasheets/t-series/communication/stream-mode
    Stream-Out:
        https://labjack.com/support/datasheets/t-series/communication/stream-mode/stream-out
    Digital I/O:
        https://labjack.com/support/datasheets/t-series/digital-io
    DAC:
        https://labjack.com/support/datasheets/t-series/dac

"""
import sys
from time import sleep

from labjack import ljm
import ljm_stream_util


def openLJMDevice(deviceType, connectionType, identifier):
    try:
        handle = ljm.open(deviceType, connectionType, identifier)
    except ljm.LJMError:
        print(
            "Error calling ljm.open(" +
            "deviceType=" + str(deviceType) + ", " +
            "connectionType=" + str(connectionType) + ", " +
            "identifier=" + identifier + ")"
        )
        raise

    return handle


def printDeviceInfo(handle):
    info = ljm.getHandleInfo(handle)
    print(
        "Opened a LabJack with Device type: %i, Connection type: %i,\n"
        "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i\n" %
        (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5])
    )


def main():
    scanRate = 1000
    scansPerRead = int(scanRate / 2)
    # Number of seconds to stream out waveforms
    runTime = 5
    # The desired stream channels
    # Up to 4 out-streams can be ran at once
    scanListNames = ["STREAM_OUT0"]
    scanList = ljm.namesToAddresses(len(scanListNames), scanListNames)[0]
    # Only stream out to DAC0
    targetAddr = 1000
    # Stream out index can only be a number between 0-3
    streamOutIndex = 0
    samplesToWrite = 512
    # Make an arbitrary waveform that increases voltage linearly from 0-2.5V
    writeData = []
    for i in range(samplesToWrite):
        sample = 2.5*i/samplesToWrite
        writeData.append(sample)

    print("Beginning...\n")
    handle = openLJMDevice(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
    printDeviceInfo(handle)

    try :
        print("\nInitializing stream out... \n")
        ljm.periodicStreamOut(handle, streamOutIndex, targetAddr, scanRate, len(writeData), writeData)
        actualScanRate = ljm.eStreamStart(handle, scansPerRead, len(scanList), scanList, scanRate)
        print("Stream started with scan rate of %f Hz\n Running for %d seconds\n" % (scanRate, runTime))
        sleep(runTime)

    except ljm.LJMError:
        ljm_stream_util.prepareForExit(handle)
        raise
    except Exception:
        ljm_stream_util.prepareForExit(handle)
        raise

    ljm_stream_util.prepareForExit(handle)


if __name__ == "__main__":
    main()
