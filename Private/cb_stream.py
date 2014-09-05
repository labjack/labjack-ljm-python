"""
Demonstrates how to stream using the eStream functions.

Not working
"""

""" Last test code in LJM wrapper in case for future work. """
"""
 * Name: LJM_SetStreamCallback
 * Desc: Sets a callback that is called by LJM when the stream has collected
 *       ScansPerRead scans.
 * Para: Handle, a valid handle to an open device.
 *       Callback, the callback function for LJM's stream thread to call
 *           when stream data is ready, which should call LJM_eStreamRead to
 *           acquire data.
 *       Arg, the user-defined argument that is passed to Callback when it is
 *           invoked.
 * Note: LJM_SetStreamCallback should be called after LJM_eStreamStart.
 * Note: LJM_eStreamStop may be called at any time when using
 *       LJM_SetStreamCallback, but the Callback function should not try to
 *       stop stream. If the Callback function detects that stream needs to be
 *       stopped, it should signal to a different thread that stream should be
 *       stopped.
 * Note: To disable the previous callback for stream reading, pass 0 or NULL as
 *       Callback.
"""
"""
#Test and finish
#typedef void (*LJM_StreamReadCallback)(void *);
#LJM_ERROR_RETURN LJM_SetStreamCallback(int Handle,LJM_StreamReadCallback Callback, void * Arg);
STREAM_READ_CALLBACK = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
def setStreamCallback(handle, callback, arg):
    #Check that callback is a function with a one value argument
    #cCB = ctypes.c_void_p(callback)
    #cArg = ctypes.c_void_p(arg)

    #error = _staticLib.LJM_SetStreamCallback(handle, cCB, cArg) #not sure yet
    #_staticLib.LJM_SetStreamCallback.argtypes = [ctypes.c_int, STREAM_READ_CALLBACK, ctypes.c_int]
    #cArg = ctypes.c_void_p.from_address(id(arg))
    #cArg = ctypes.c_void_p(arg)
    #cArg = ctypes.POINTER(ctypes.c_double)(ctypes.c_double(arg))
    error = _staticLib.LJM_SetStreamCallback(handle, STREAM_READ_CALLBACK(callback), ctypes.byref(arg)) #not sure yet
    if error != errorcodes.NOERROR:
        raise LJMError(error)
"""



from labjack import ljm
import time
import sys
from datetime import datetime
import traceback
import ctypes

#Class to hold our stream information
class StreamInfo:
    def __init__(self):
        self.handle = 0
        self.scanRate = 0
        self.scansPerRead = 0
        self.streamLengthMS = 0
        self.done = 0
        #LJM_StreamReadCallback callback;
        
        self.numAddresses = 0
        self.aScanList = 0
        self.aScanListNames = 0
        
        self.aDataSize = 0
        self.aData = 0

        """
        handle, scanRate, scansPerRead, streamLengthMS, done, numAddresses, aScanList, aScanListNames, aDataSize, aData):
        
        self.handle = handle
        self.scanRate = scanRate
        self.scansPerRead = scansPerRead
        self.streamLengthMS = streamLengthMS
        self.done = done
        #LJM_StreamReadCallback callback;
        
        self.numAddresses = numAddresses
        self.aScanList = aScanList
        self.aScanListNames = aScanListNames
        
        self.aDataSize = aDataSize
        self.aData = aData
        """

def test(arg):
    pass
    #print(str(arg))

#Function to pass to the callback function
def myStreamReadCallback(arg):
    print("here")

    #Check arg
    si = arg #In this example, we expect arg to be a StreamInfo object
    streamRead = 0
    deviceScanBacklog = 0
    err = 0
    numScansInLJMBuffer = 0
    
    #Check if stream is done so that we don't output the printf below
    numScansInLJMBuffer = si.scansPerRead;
    if si.done:
        return
    
    print(str(streamRead) + ".\n")
    
    numScansInLJMBuffer = si.scansPerRead
    while numScansInLJMBuffer >= si.scansPerRead:
        #Check if stream is done so that we don't loop here past the expected
        #program length
        if si.done:
            return;
        
        try:
            aData, deviceScanBacklog, LJMScanBacklog = ljm.eStreamRead(handle)
            print("    ");
            #HardcodedPrintScans(si->channelNames, si->aData, si->scansPerRead, si->numChannels,
            #    deviceScanBacklog, LJMScanBacklog);
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            
            #If LJM has called this callback, the data is valid, but LJM_eStreamRead
            #may return LJME_STREAM_NOT_RUNNING if another thread has stopped stream,
            #such as this example program does in StreamWithCallback().
            if ljme.errorCode != ljm.errorcodes.STREAM_NOT_RUNNING:
                print("LJM_eStreamRead: " + str(ljme));

        numScansInLJMBuffer = LJMScanBacklog;

    
#Main code
MAX_REQUESTS = 50 # The number of eStreamRead calls that will be performed.
EXTERNAL_STREAM_CLOCK = False # Set to True for external stream clock.
FIO0_PULSE_OUT = False # Set FIO to pulse out.

si = StreamInfo()

# Open first found LabJack
si.handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctUSB, "ANY")
#handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(si.handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Stream Configuration
si.aScanListNames = ["AIN0",  "FIO_STATE",  "SYSTEM_TIMER_20HZ", "STREAM_DATA_CAPTURE_16"] #Scan list names to stream
si.scanRate = 2000
si.scansPerRead = si.scanRate/2
si.streamLengthMS = 1000
si.done = False
si.numAddresses = len(si.aScanListNames)
si.aScanList = ljm.namesToAddresses(si.numAddresses, si.aScanListNames)[0]
si.aDataSize - si.numAddresses * si.scansPerRead
#si = StreamInfo(handle, scanRate, scansPerRead, streamLengthMS, done, numChannels, aScanList, aScanListNames, aDataSize, aData)

if EXTERNAL_STREAM_CLOCK:
    ljm.eWriteName(si.handle, "STREAM_OPTIONS", 2)
    ljm.eWriteName(si.handle, "STREAM_EXTERNAL_CLOCK_DIVISOR", 1)

if FIO0_PULSE_OUT:
    # If you do not have a signal generator of some sort, you can connect a
    # wire from FIO0 to CIO3 and call EnableFIO0PulseOut to verify
    # that your program is working.
    
    # Set FIO0 to do a 50% duty cycle
    # http://labjack.com/support/datasheets/t7/digital-io/extended-features/pulse-out
    pulseRate = si.scanRate
    numPulses = si.scanRate * si.streamLengthMS / 1000 + 5000
    rollValue = 10000000 / pulseRate #10 MHz / pulseRate
    
    print("Enabling " + numPulses + " pulses on FIO0 at a " + pulseRate + " Hz pulse rate");
    
    ljm.eWriteName(si.handle, "DIO0_EF_ENABLE", 0)
    ljm.eWriteName(si.handle, "DIO_EF_CLOCK0_DIVISOR", 8)
    ljm.eWriteName(si.handle, "DIO_EF_CLOCK0_ROLL_VALUE", rollValue)
    ljm.eWriteName(si.handle, "DIO_EF_CLOCK0_ENABLE", 1)
    ljm.eWriteName(si.handle, "DIO0", 0)
    ljm.eWriteName(si.handle, "DIO0_EF_TYPE", 2)
    ljm.eWriteName(si.handle, "DIO0_EF_VALUE_A", 5000)
    ljm.eWriteName(si.handle, "DIO0_EF_VALUE_B", 0)
    ljm.eWriteName(si.handle, "DIO0_EF_VALUE_C", numPulses)
    ljm.eWriteName(si.handle, "DIO0_EF_ENABLE", 1)

print myStreamReadCallback
try:
    t0 = datetime.now()

    # Configure and start stream
    scanRate = ljm.eStreamStart(si.handle, si.scansPerRead, si.numAddresses, si.aScanList, si.scanRate)
    si.scanRate = scanRate #Actual scan rate
    print("\nStream started with a scan rate of %0.0f Hz." % si.scanRate)

    #ljm.setStreamCallback(si.handle, myStreamReadCallback, ctypes.cast(si, ctypes.POINTER(StreamInfo)))
    #ljm.setStreamCallback(si.handle, myStreamReadCallback, si)
    t = 9
    ljm.setStreamCallback(si.handle, test, ctypes.c_double(t)) #ctypes.cast(9.0, ctypes.POINTER(ctypes.c_double)))


    print("Stream running, callback set, sleeping for " + str(si.streamLengthMS) + " milliseconds\n", )
    time.sleep(si.streamLengthMS/1000.0)
except ljm.LJMError:
    
    #TODO: FIGURE OUT HOW TO PRINT THE STACKTRACE
    ljme = sys.exc_info()[1]
    st = sys.exc_info()[2]
    #print("LJM Exception: " + str(ljme))
    print("\nLJM Exception:\n" + "".join(i for i in traceback.format_exc()))
    #print(st)
    #traceback.print_stack()

except Exception:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    print("\nException:\n" + "".join('  ' + i for i in lines))
    #or
    """
    print("\nException:\n" + str(traceback.format_exc()))
    #or
    e = sys.exc_info()[1]
    st = sys.exc_info()[2]
    print("\nException:\n" + "".join(i for i in traceback.format_exc()))
    """
    
print("\nStopping Stream...")
si.done = True
ljm.eStreamStop(si.handle)
t1 = datetime.now()

print("Stream stopped. " + str((t1-t0).seconds*1000 + float((t1-t0).microseconds)/1000) + " milliseconds have elapsed since eStreamStart\n")

# Close handle
ljm.close(si.handle)
