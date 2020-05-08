"""
Demonstrates setting up stream-in with stream-out that continuously updates.

Note: the LJM aperiodic stream-out functions are recommended for
    most use cases that require aperiodic stream-out

Streams in while streaming out arbitrary values. These arbitrary stream-out
values act on DAC0 to alternate between increasing the voltage from 0 to 2.5 and
decreasing from 5.0 to 2.5 on (approximately). Though these values are initially
generated during the call to createOutContext, the values could be
dynamically generated, read from a file, etc. To convert this example file into
a program to suit your needs, the primary things you need to do are:

    1. Edit the global setup variables in this file
    2. Define your own createOutContext function or equivalent
    3. Define your own processStreamResults function or equivalent

You may also need to configure AIN, etc.

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
    Analog Inputs:
        https://labjack.com/support/datasheets/t-series/ain
    Stream-Out:
        https://labjack.com/support/datasheets/t-series/communication/stream-mode/stream-out/stream-out-description
    Digital I/O:
        https://labjack.com/support/datasheets/t-series/digital-io
    DAC:
        https://labjack.com/support/datasheets/t-series/dac

"""
import sys

from labjack import ljm
import ljm_stream_util


# Setup

inNames = ["AIN0", "AIN1"]

"""
streamOuts = [
    {
        "target": str register name that stream-out values will be sent to,
        "bufferNumBytes": int size in bytes for this stream-out buffer,

        "streamOutIndex": int STREAM_OUT# offset. 0 would generate names like
            "STREAM_OUT0_BUFFER_STATUS", etc.

        "setLoop": int value to be written to STREAM_OUT#(0:3)_setLoop
    },
    ...
]
"""
streamOuts = [
    {
        "target": "DAC0",
        "bufferNumBytes": 512,
        "streamOutIndex": 0,
        "setLoop": 2
    },
    {
        "target": "DAC1",
        "bufferNumBytes": 512,
        "streamOutIndex": 1,
        "setLoop": 3
    }
]

initialScanRateHz = 200
# Note: This program does not work well for large scan rates because
# the value loops will start looping before new value loops can be written.
# While testing on USB with 512 bytes in one stream-out buffer, 2000 Hz worked
# without stream-out buffer loop repeating.
# (Other machines may have different results.)
# Increasing the size of the bufferNumBytes will increase the maximum speed.
# Using an Ethernet connection type will increase the maximum speed.

numCycles = initialScanRateHz / 10
numCycles_MIN = 10
if numCycles < numCycles_MIN:
    numCycles = numCycles_MIN


def printRegisterValue(handle, registerName):
    value = ljm.eReadName(handle, registerName)
    print("%s = %f" % (registerName, value))


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


def main(
    initialScanRateHz=initialScanRateHz,
    inNames=inNames,
    streamOuts=streamOuts,
    numCycles=numCycles
):
    print("Beginning...")
    handle = openLJMDevice(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
    printDeviceInfo(handle)

    print("Initializing stream out buffers...")
    outContexts = []
    for streamOut in streamOuts:
        outContext = ljm_stream_util.createOutContext(streamOut)
        ljm_stream_util.initializeStreamOut(handle, outContext)
        outContexts.append(outContext)

    print("")

    for outContext in outContexts:
        printRegisterValue(handle, outContext["names"]["bufferStatus"])

    for outContext in outContexts:
        updateStr = "Updating %(streamOut)s buffer whenever " \
            "%(bufferStatus)s is greater or equal to " % outContext["names"]
        print(updateStr + str(outContext["stateSize"]))

    scansPerRead = int(min([context["stateSize"] for context in outContexts]))
    bufferStatusNames = [out["names"]["bufferStatus"] for out in outContexts]
    try:
        scanList = ljm_stream_util.createScanList(
            inNames=inNames,
            outContexts=outContexts
        )
        print("scanList: " + str(scanList))
        print("scansPerRead: " + str(scansPerRead))

        scanRate = ljm.eStreamStart(handle, scansPerRead, len(scanList),
                                     scanList, initialScanRateHz)
        print("\nStream started with a scan rate of %0.0f Hz." % scanRate)
        print("\nPerforming %i buffer updates." % numCycles)

        iteration = 0
        totalNumSkippedScans = 0
        while iteration < numCycles:
            bufferStatuses = [0]
            infinityPreventer = 0
            while max(bufferStatuses) < outContext["stateSize"]:
                bufferStatuses = ljm.eReadNames(
                    handle,
                    len(bufferStatusNames),
                    bufferStatusNames
                )
                infinityPreventer = infinityPreventer + 1
                if infinityPreventer > scanRate:
                    raise ValueError(
                        "Buffer statuses don't appear to be updating:" +
                        str(bufferStatusNames) + str(bufferStatuses)
                    )

            for outContext in outContexts:
                ljm_stream_util.updateStreamOutBuffer(handle, outContext)

            # ljm.eStreamRead will sleep until data has arrived
            streamRead = ljm.eStreamRead(handle)

            numSkippedScans = ljm_stream_util.processStreamResults(
                iteration,
                streamRead,
                inNames,
                deviceThreshold=outContext["stateSize"],
                LJMThreshold=outContext["stateSize"]
            )
            totalNumSkippedScans += numSkippedScans

            iteration = iteration + 1
    except ljm.LJMError:
        ljm_stream_util.prepareForExit(handle)
        raise
    except Exception:
        ljm_stream_util.prepareForExit(handle)
        raise

    ljm_stream_util.prepareForExit(handle)

    print("Total number of skipped scans: %d" % totalNumSkippedScans)


if __name__ == "__main__":
    main()
