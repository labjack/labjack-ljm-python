"""
Demonstrates usage of the periodic stream-out functions.

Streams out arbitrary values. These arbitrary values act on DAC0 to cyclically
increase the voltage from 0 to 2.5 V.

Note: This example requires LJM 1.21 or higher.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    LJM Single Value Functions (such as eReadName and eReadAddress):
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
import sys
from time import sleep

from labjack import ljm


def main():
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

    scanRate = 1000  # Scans per second
    scansPerRead = int(scanRate / 2)
    runTimeS = 5.0  # Number of seconds to stream out waveforms

    # The desired stream channels. Up to 4 out-streams can be ran at once.
    scanListNames = ["STREAM_OUT0"]  # Scan list names to stream.
    scanList = ljm.namesToAddresses(len(scanListNames), scanListNames)[0]

    targetAddr = 1000  # Stream out to DAC0.

    # Stream out index can be a value of 0 to 3.
    streamOutIndex = 0

    # Make an arbitrary waveform that increases voltage linearly from
    # 0 to 2.5 V.
    samplesToWrite = 512
    writeData = []
    for i in range(samplesToWrite):
        sample = 2.5*i/samplesToWrite
        writeData.append(sample)

    try :
        print("\nInitializing stream out...\n")
        ljm.periodicStreamOut(handle, streamOutIndex, targetAddr, scanRate, len(writeData), writeData)
        print("Beginning stream out...\n")
        actualScanRate = ljm.eStreamStart(handle, scansPerRead, len(scanList), scanList, scanRate)
        print("Stream started with scan rate of %f Hz." % actualScanRate)
        print("  Running for %d seconds.\n" % runTimeS)
        sleep(runTimeS)
    except ljm.LJMError:
        ljme = sys.exc_info()[1]
        print(ljme)
    except Exception:
        e = sys.exc_info()[1]
        print(e)

    try:
        print("Stopping Stream...")
        ljm.eStreamStop(handle)
    except ljm.LJMError:
        ljme = sys.exc_info()[1]
        print(ljme)
    except Exception:
        e = sys.exc_info()[1]
        print(e)


if __name__ == "__main__":
    main()
