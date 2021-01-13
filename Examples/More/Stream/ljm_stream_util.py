
from time import sleep

from labjack import ljm


def calculateSleepFactor(scansPerRead, LJMScanBacklog):
    """Calculates how much sleep should be done based on how far behind stream is.

    @para scansPerRead: The number of scans returned by a eStreamRead call
    @type scansPerRead: int
    @para LJMScanBacklog: The number of backlogged scans in the LJM buffer
    @type LJMScanBacklog: int
    @return: A factor that should be multiplied the normal sleep time
    @type: float
    """
    DECREASE_TOTAL = 0.9
    portionScansReady = float(LJMScanBacklog) / scansPerRead
    if (portionScansReady > DECREASE_TOTAL):
        return 0.0
    return (1 - portionScansReady) * DECREASE_TOTAL


def variableStreamSleep(scansPerRead, scanRate, LJMScanBacklog):
    """Sleeps for approximately the expected amount of time until the next scan
    is ready to be read.

    @para scansPerRead: The number of scans returned by a eStreamRead call
    @type scansPerRead: int
    @para scanRate: The stream scan rate
    @type scanRate: numerical
    @para LJMScanBacklog: The number of backlogged scans in the LJM buffer
    @type LJMScanBacklog: int
    """
    sleepFactor = calculateSleepFactor(scansPerRead, LJMScanBacklog)
    sleepTime = sleepFactor * scansPerRead / float(scanRate)
    sleep(sleepTime)


def convertNameToIntType(name):
    return ljm.nameToAddress(name)[1]


def convertNameToOutBufferTypeStr(targetName):
    OUT_BUFFER_TYPE_STRINGS = {
        ljm.constants.UINT16: "U16",
        ljm.constants.UINT32: "U32",
        # Note that there is no STREAM_OUT#(0:3)_BUFFER_I32
        ljm.constants.FLOAT32: "F32"
    }
    intType = convertNameToIntType(targetName)
    return OUT_BUFFER_TYPE_STRINGS[intType]


def convertNameToAddress(name):
    return ljm.nameToAddress(name)[0]


def convertNamesToAddresses(names, lengthLimit=None):
    """Convert a list of names to a list of addresses using LJM.

    @para names: Names to be converted to addresses.
    @type names: iterable over str
    @para lengthLimit: Limit the number of names to read from the name array
        also limit the size of the returned addresses.
    @type lengthLimit: int
    @return: The given names converted to addresses.
    @rtype: iterable over str
    """
    length = len(names)
    if lengthLimit:
        length = lengthLimit

    addressesAndTypes = ljm.namesToAddresses(length, names)

    # ljm.namesToAddresses returns a tuple of a list of addresses and a list of
    # types. The list of addresses is indexed at 0 of that tuple.
    return addressesAndTypes[0]


def createScanList(inNames=[], outContexts=[]):
    """Creates a list of integer addresses from lists of in and out names."""
    inAddresses = []
    outAddresses = []

    if len(outContexts) > 4:
        raise ValueError("The T-Series only has 4 stream-out buffers")

    for outContext in outContexts:
        streamOutName = outContext["names"]["streamOut"]
        streamOutAddress = convertNameToAddress(streamOutName)
        outAddresses.append(streamOutAddress)

    if inNames:
        inAddresses = convertNamesToAddresses(inNames)

    return inAddresses + outAddresses


def generateState(start, diff, stateSize, stateName):
    """Generates a dict that contains a stateName and a list of values."""
    values = []
    increment = float(1) / stateSize
    for iteration in range(int(stateSize)):
        # Get a value between start + diff
        sample = start + diff * increment * iteration
        values.append(sample)

    return {
        "stateName": stateName,
        "values": values
    }


def createOutContext(streamOut):
    """Create an object which describes some stream-out buffer states.

    Create dict which will look something like this:
    outContext = {
        "currentIndex": int tracking which is the current state,
        "states": [
            {
                "stateName": str describing this state,
                "values": iterable over float values
            },
            ...
        ],
        "stateSize": int describing how big each state's "values" list is,
        "targetTypeStr": str used to generate this dict's "names" list,
        "target": str name of the register to update during stream-out,
        "bufferNumBytes": int number of bytes of this stream-out buffer,
        "streamOutIndex": int number of this stream-out,
        "setLoop": int number to be written to to STREAM_OUT#(0:3)_SET_LOOP,
        "names": dict of STREAM_OUT# register names. For example, if
            "streamOutIndex" is 0 and "targetTypeStr" is "F32", this would be
        {
            "streamOut": "STREAM_OUT0",
            "target": "STREAM_OUT0_TARGET",
            "bufferSize": "STREAM_OUT0_BUFFER_SIZE",
            "loopSize": "STREAM_OUT0_LOOP_SIZE",
            "setLoop": "STREAM_OUT0_SET_LOOP",
            "bufferStatus": "STREAM_OUT0_BUFFER_STATUS",
            "enable": "STREAM_OUT0_ENABLE",
            "buffer": "STREAM_OUT0_BUFFER_F32"
        }
    }
    """
    BYTES_PER_VALUE = 2
    outBufferNumValues = streamOut["bufferNumBytes"] / BYTES_PER_VALUE

    # The size of all the states in outContext. This must be half of the
    # out buffer or less. (Otherwise, values in a given loop would be getting
    # overwritten during a call to updateStreamOutBuffer.)
    stateSize = outBufferNumValues / 2

    targetType = convertNameToOutBufferTypeStr(streamOut["target"])
    outContext = {
        "currentIndex": 0,
        "states": [],
        "stateSize": stateSize,
        "targetTypeStr": targetType
    }
    outContext.update(streamOut)

    outContext["names"] = createStreamOutNames(outContext)

    outContext["states"].append(
        generateState(
            0.0,
            2.5,
            stateSize,
            "increase from 0.0 to 2.5"
        )
    )
    outContext["states"].append(
        generateState(
            5.0,
            -2.5,
            stateSize,
            "decrease from 5.0 to 2.5"
        )
    )

    return outContext


def createStreamOutNames(outContext):
    return {
        "streamOut":
            "STREAM_OUT%(streamOutIndex)d" % outContext,

        "target":
            "STREAM_OUT%(streamOutIndex)d_TARGET" % outContext,

        "bufferSize":
            "STREAM_OUT%(streamOutIndex)d_BUFFER_SIZE" % outContext,

        "loopSize":
            "STREAM_OUT%(streamOutIndex)d_LOOP_SIZE" % outContext,

        "setLoop":
            "STREAM_OUT%(streamOutIndex)d_SET_LOOP" % outContext,

        "bufferStatus":
            "STREAM_OUT%(streamOutIndex)d_BUFFER_STATUS" % outContext,

        "enable":
            "STREAM_OUT%(streamOutIndex)d_ENABLE" % outContext,

        "buffer":
            "STREAM_OUT%(streamOutIndex)d_BUFFER_%(targetTypeStr)s" % outContext
    }


def updateStreamOutBuffer(handle, outContext):
    # Write values to the stream-out buffer. Note that once a set of values have
    # been written to the stream out buffer (STREAM_OUT0_BUFFER_F32, for
    # example) and STREAM_OUT#_SET_LOOP has been set, that set of values will
    # continue to be output in order and will not be interrupted until their
    # "loop" is complete. Only once that set of values have been output in their
    # entirety will the next set of values that have been set using
    # STREAM_OUT#_SET_LOOP start being used.

    outNames = outContext["names"]

    ljm.eWriteName(handle, outNames["loopSize"], outContext["stateSize"])

    stateIndex = outContext["currentIndex"]
    errorAddress = -1
    currentState = outContext["states"][stateIndex]
    values = currentState["values"]

    info = ljm.getHandleInfo(handle)
    maxBytes = info[5]
    SINGLE_ARRAY_SEND_MAX_BYTES = 520
    if maxBytes > SINGLE_ARRAY_SEND_MAX_BYTES:
        maxBytes = SINGLE_ARRAY_SEND_MAX_BYTES

    NUM_HEADER_BYTES = 12
    NUM_BYTES_PER_F32 = 4
    maxSamples = int((maxBytes - NUM_HEADER_BYTES) / NUM_BYTES_PER_F32)

    start = 0
    while start < len(values):
        numSamples = len(values) - start
        if numSamples > maxSamples:
            numSamples = maxSamples
        end = start + numSamples
        writeValues = values[start:end]

        ljm.eWriteNameArray(handle, outNames["buffer"], numSamples, writeValues)

        start = start + numSamples

    ljm.eWriteName(handle, outNames["setLoop"], outContext["setLoop"])

    print("  Wrote " +
          outContext["names"]["streamOut"] +
          " state: " +
          currentState["stateName"]
          )

    # Increment the state and wrap it back to zero
    outContext["currentIndex"] = (stateIndex + 1) % len(outContext["states"])


def initializeStreamOut(handle, outContext):
    # Allocate memory for the stream-out buffer
    outAddress = convertNameToAddress(outContext["target"])
    names = outContext["names"]
    ljm.eWriteName(handle, names["target"], outAddress)
    ljm.eWriteName(handle, names["bufferSize"], outContext["bufferNumBytes"])
    ljm.eWriteName(handle, names["enable"], 1)

    updateStreamOutBuffer(handle, outContext)


def processStreamResults(
    iteration,
    streamRead,
    inNames,
    deviceThreshold=0,
    LJMThreshold=0
):
    """Print ljm.eStreamRead results and count the number of skipped samples."""
    data = streamRead[0]
    deviceNumBacklogScans = streamRead[1]
    LJMNumBacklogScans = streamRead[2]
    numAddresses = len(inNames)
    numScans = len(data) / numAddresses

    # Count the skipped samples which are indicated by -9999 values. Missed
    # samples occur after a device's stream buffer overflows and are
    # reported after auto-recover mode ends.
    numSkippedSamples = data.count(-9999.0)

    print("\neStreamRead %i" % iteration)
    resultStrs = []
    for index in range(len(inNames)):
        resultStrs.append("%s = %0.5f" % (inNames[index], data[index]))

    if resultStrs:
        print("  1st scan out of %i: %s" % (numScans, ", ".join(resultStrs)))

    # This is a test to ensure that 2 in channels are synchronized
    # def print_if_not_equiv_floats(index, a, b, delta=0.01):
    #     diff = abs(a - b)
    #     if diff > delta:
    #         print("index: %d, a: %0.5f, b: %0.5f, diff: %0.5f, delta: %0.5f" % \
    #             (index, a, b, diff, delta)
    #         )

    # for index in range(0, len(data), 2):
    #     print_if_not_equiv_floats(index, data[index], data[index + 1])

    if numSkippedSamples:
        print(
            "  **** Samples skipped = %i (of %i) ****" %
            (numSkippedSamples, len(data))
        )

    statusStrs = []
    if deviceNumBacklogScans > deviceThreshold:
        statusStrs.append("Device scan backlog = %i" % deviceNumBacklogScans)
    if LJMNumBacklogScans > LJMThreshold:
        statusStrs.append("LJM scan backlog = %i" % LJMNumBacklogScans)

    if statusStrs:
        statusStr = "  " + ",".join(statusStrs)
        print(statusStr)

    return numSkippedSamples


def prepareForExit(handle, stopStream=True):
    if stopStream:
        print("\nStopping Stream")
        try:
            ljm.eStreamStop(handle)
        except ljm.LJMError as exception:
            if exception.errorString != "STREAM_NOT_RUNNING":
                raise

    ljm.close(handle)
