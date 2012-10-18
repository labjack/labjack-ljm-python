"""
Multip-Platform Python wrapper for the LJModbus driver.

"""
import ctypes
import os
import struct

PYTHON_VERSION = 0.01

## LJM Exception
class LJMError(Exception):
    """
    Custom Exception meant for dealing with LJM specific errors
    """
    def __init__(self, error_code = None, error_frame = None, error_string = ""):
        self._error_code = error_code
        self._error_frame = error_frame
        self._error_string = error_string
        if not self._error_string:
            try:
                self._error_string = LJM_ErrorToString(error_code)
            except:
                self._error_string = error_code #str(self.error_code)
        #self.message = self.__str__()
        #Exception(self._get_message())

    @property
    def error_code(self):
        return self._error_code

    @property
    def error_frame(self):
        return self._error_frame

    @property
    def error_string(self):
        return self._error_string
    
    def __str__(self):
        if self._error_frame is None:
            fr_str = ""
        else:
            fr_str = "Frame " + str(self._error_frame) + ", "
        if self._error_string.find("The error constants file") != -1 and self._error_string.find("could not be opened") != -1:
            err_str = "Error " + str(self._error_code)
        else:
            err_str = str(self._error_string)
        return fr_str + err_str
## LJM Exception end

### Load LJModbus library
def _load_library():
    """
    _ljm_load_library()
    Returns a ctypes dll pointer to the library.
    """
    try:
        if(os.name == "posix"):
            try:
                #Linux
                return ctypes.CDLL("LabJackM.so")
            except OSError, e:
                pass # May be on Mac.
            except Exception, e:
                raise LJMError(error_string = ("Cannot load the LJM Linux SO.  " + str(e)))
            
            try:
                return ctypes.CDLL("libLabJackM.dylib")
            except OSError, e:
                raise LJMError(error_string = ("Cannot load the LJM driver.  Check that the driver is installed.  " + str(e)))
            except Exception, e:
                raise LJMError(error_string = ("Cannot load the LJM Mac OS X Dylib.  " + str(e)))
        if(os.name == "nt"):
            #Windows
            try:
                #Win
                #return ctypes.WinDLL("LabJackM.dll")
                return ctypes.CDLL("LabJackM.dll")
                #[Error 22] This application has failed to start because the application configuration is incorrect. Reinstalling the application may fix this problem
                #return ctypes.windll.LoadLibrary("LJModbus")
                #return ctypes.CDLL("LJModbus.dll")
            except Exception, e:
                raise LJMError(error_string = ("Cannot load LJM driver.  " + str(e)))
    except LJMError, e:
        print str(type(e)) + ": " + str(e)
        return None

static_lib = _load_library()
### Load LJModbus library end

### Classes



## Device Types
class DeviceType:
    UE9 = 9
    U3 = 3
    U6 = 6
## Device Types end

## Connection Types
class ConnectionType:
    USB = 1
    ETHERNET = 2
    ETHERNET_MB = 3
## Connection Types end

## Device
class Device(object):

    def __init__(self, device_type=None, connection_type=None, identifier=None, debug=False, autoOpen=True): #handle=None, deviceType=None, connectionType=None, device=None):
        self.handle = None
        if autoOpen:
            self.open(**kargs)
        
        '''
        if device != None:
            self.handle = device.handle
            self.device_type = device.deviceType
            self.connection_type = device.connectionType
        else:
            self.handle = handle
            self.device_type = deviceType
            self.connection_type = connectionType
        '''
    
    '''
    def __del__(self):
        if handle != None:
            #Close the existing handle
            LJM_Close(handle)
    '''
    
    '''    
    def OpenFirstFound(self, deviceType, connectionType):
        error, self.handle = LJM_OpenFirstFound(deviceType, connectionType)
        self._handle_ljm_error(error)
        self.device_type = deviceType
        self.connection_type = connectionType
    '''
    def open(self, device_type=None, connection_type=None, identifier=None):
        '''
        if device_type is None:
            if connection_type is not None:
                if type(connection_type) is None

            else:
                device_type = 0
                connection_type = 0
        
        
        if connection_type is None:
            if device_type is None:
                device_type = 0
            
                connection_type = 0
                
        if identifier is None:
            identifier = "0"
        identifier = str(identifier)

        if device_type
        self.handle = LJM_OpenS(device_type, connection_type, identifier)
        '''
        return 1
    
    
    #LJM_Close
    
    """
    def open(self, deviceType, connectionType, firstFound=True, serialNumber=None, ipAddress=None, name=None, port=52360):
        if self.handle != None:
            #Close the existing handle
            LJM_Close(self.handle)
            self.handle = None
        
        error = 0
        if firstFound:
            error, self.handle = LJM_OpenFirstFound(deviceType, connectionType)
            #print "here"
        elif serialNumber != None:
            if isinstance(serialNumber, str):
                error, self.handle = LJM_OpenByStringSN(serialNumber, deviceType, connectionType, port)
            else:
                error, self.handle = LJM_OpenByLongSN(serialNumber, deviceType, connectionType, port)
        elif ipAddress != None:
            if isinstance(ipAddress, str):
                error, self.handle = LJM_OpenByStringIP(ipAddress, deviceType, connectionType, port)
            else:
                error, self.handle = LJM_OpenByLongIP(ipAddress, deviceType, connectionType, port)
        elif name != None:
            error, self.handle = LJM_OpenByName(name, deviceType, connectionType, port)
        else:
            error = 1007 #No device was specified LJE_LABJACK_NOT_FOUND

        self._handle_ljm_error(error)
        self.device_type = deviceType
        self.connection_type = connectionType
        
    def feedback(self, unitID, numCommands, write, regAddress, numRegs, data):
        error, data_r, error_frame = LJM_Feedback(self.handle, unitID, numCommands, write, regAddress, numRegs, data)
        self._handle_ljm_error(error)
        return data_r, error_frame

    def readMultipleBytes(self, unitID, regAddress, numRegs):
        error, data = LJM_ReadMultipleBytes(self.handle, unitID, regAddress, numRegs)
        self._handle_ljm_error(error)
        return data

    def writeMultipleBytes(self, unitID, regAddress, numRegs, data):
        #LJM_WriteMultipleBytes(self.handle, unit_id, reg_address, num_regs, data_list)
        error = LJM_WriteMultipleBytes(self.handle, unitID, regAddress, numRegs, data)
        self._handle_ljm_error(error)
    """
## Device end

### Classes end

### Helper functions - take out if finalized driver provides these
'''
def convert_list_to_float(list, endian='>'):
    #args: endian = The endian of the list.  '>' = big, '<' = little.
    return convert_list_to_value(list, 'f', 4, endian)

def convert_float_to_list(value, endian='>'):
    return convert_value_to_list(float(value), 'f', 4, endian)

def convert_list_to_uint32(list, endian='>'):
    return convert_list_to_value(list, 'I', 4, endian)

def convert_uint32_to_list(value, endian='>'):
    return convert_value_to_list(value, 'I', 4, endian)

def convert_list_to_uint16(list, endian='>'):
    return convert_list_to_value(list, 'H', 2, endian)

def convert_uint16_to_list(value, endian='>'):
    return convert_value_to_list(value, 'H', 2, endian)

def convert_list_to_value(list, format, size, endian):
    return struct.unpack(endian + format, struct.pack(endian + 'B'*size, *(list[:size])))[0]

def convert_value_to_list(value, format, size, endian):
    return list(struct.unpack(endian + 'B'*size, struct.pack(endian + format, value))[:size])
'''
### Helper functions end

## Private Helper functions

def _convert_list_to_ctype_list(li, c_type):
    ctypes.memmove
    c_list = (c_type*len(li))(0)
    for i in range(len(li)):
        c_list[i] = c_type(li[i])
        #print str(list[i]) + ", " + str(c_list[i])
    return c_list

def _convert_string_list_to_ctype_list(li):
    #figure out the 2D size
    size2 = max(len(x) for x in li) + 1
    c_list = (ctypes.c_char*size2*len(li))()
    for i in range(len(li)):
        c_list[i].value = li[i]
    return c_list
        #for j in range(len(li[i])):
        #    c_list[i][j] = ctypes.c_char(li[i][j])
    '''
    c_list = (ctypes.c_char_p * len(li))()
    c_list[:] = ctypes.create_string_buffer(li, size2)
    return c_list
    '''

def _convert_ctype_list_to_list(list_ctype):
    #print list_cbyte
    #for i in list_cbyte:
    #    print i
    return [i for i in list_ctype]

'''
def _convert_list_ctype_to_list(list_c_type):
    return [i.value for i in list_cubyte]

def _convert_list_to_list_cubyte(list):
    c_list = (ctypes.c_ubyte*len(list))()
    for i in range(0, len(list), 1):
        c_list[i] = ctypes.c_ubyte(list[i])
        #print str(list[i]) + ", " + str(c_list[i])
    return c_list

def _convert_list_to_list_clong(list):
    c_list = (ctypes.c_long*len(list))()
    for i in range(0, len(list), 1):
        c_list[i] = ctypes.c_long(list[i])
        #print str(list[i]) + ", " + str(c_list[i])
    return c_list


def _convert_cubyte_list_to_list(list_cubyte):
    #print list_cbyte
    #for i in list_cbyte:
    #    print i
    return [(i & 0xFF) for i in list_cubyte]
'''

## Private Helper functions end

### Wrapper for LJModbus library

## Functions
"""
def LJM_OpenFirstFound(deviceType, connectionType):
    c_handle = ctypes.c_long()
    error = static_lib.LJM_OpenFirstFound(deviceType, connectionType, ctypes.byref(c_handle))
    return error, c_handle

def LJM_OpenByLongSN(serialNumber, deviceType, connectionType, port):
    #Not tested
    #long _stdcall LJM_OpenByLongSN(long serialNumber, long deviceType, long connectionType, long port, long * handle)
    c_handle = ctypes.c_long()
    error = static_lib.LJM_OpenByLongSN(serialNumber, deviceType, connectionType, port, ctypes.byref(handle))
    return error, c_handle

def LJM_OpenByStringSN(serialNumber, deviceType, connectionType, port):
    #Not tested
    #long _stdcall LJM_OpenByStringSN(const char * serialNumber, long deviceType, long connectionType, long port, long * handle)
    c_handle = ctypes.c_long()
    error = static_lib.LJM_OpenByStringSN(serialNumber, deviceType, connectionType, port, ctypes.byref(handle))

def LJM_OpenByLongIP(ipAddress, deviceType, connectionType, port):
    #not tested
    #long _stdcall LJM_OpenByLongIP(long ipAddress, long deviceType, long connectionType, long port, long * handle)
    c_handle = ctypes.c_long()
    error = static_lib.LJM_OpenByLongIP(ipAddress, deviceType, connectionType, port, ctypes.byref(handle))
    return error, c_handle

def LJM_OpenByStringIP(ipAddress, deviceType, connectionType, port):
    #not tested
    #long _stdcall LJM_OpenByStringIP(const char * ipAddress, long deviceType, long connectionType, long port, long * handle)
    c_handle = ctypes.c_long()
    error = static_lib.LJM_OpenByStringIP(ipAddress, deviceType, connectionType, port, ctypes.byref(handle))
    return error, c_handle

def LJM_OpenByName(name, deviceType, connectionType, port):
    #not tested
    #long _stdcall LJM_OpenByName(const char * name, long deviceType, long connectionType, long port, long * handle)
    c_handle = ctypes.c_long()
    static_lib.LJM_OpenByName(name, deviceType, connectionType, port, ctypes.byref(handle))
    return error, c_handle

'''
long _stdcall LJM_GetSerialNumber(long handle, long * serial)

long _stdcall LJM_GetName(long handle, char * name)

long _stdcall LJM_GetIPAddress(long handle, char * ipAddress)

long _stdcall LJM_GetDeviceType(long handle, long * type)
'''

#def LJM_Close(handle):
#    return static_lib.LJM_Close(handle)

def LJM_Feedback(handle, unitID, numCommands, aWrite, aRegAddress, aNumRegs, aData):
    #LJM_Feedback (long handle, long UnitID, long NumCommands, long *aReadOrWrite, long *aRegAddress, long *aNumReg, unsigned char *aData, long *ErrorFrame)
    c_write = _convert_list_to_list_clong(aWrite)
    c_reg_addr = _convert_list_to_list_clong(aRegAddress)
    c_num_reg = _convert_list_to_list_clong(aNumRegs)
    c_data = _convert_list_to_list_cbyte(aData)
    c_error_frame = ctypes.c_long()
    error = static_lib.LJM_Feedback(handle, unitID, numCommands, ctypes.byref(c_write), ctypes.byref(c_reg_addr), ctypes.byref(c_num_reg), ctypes.byref(c_data), ctypes.byref(c_error_frame))
    return error, _convert_list_cbyte_to_list(c_data), c_error_frame.value

def LJM_ReadMultipleBytes(handle, unitID, regAddress, numRegs):
    c_data = (ctypes.c_byte*(numRegs*2))(0)
    error = static_lib.LJM_ReadMultipleBytes(handle, unitID, regAddress, numRegs, ctypes.byref(c_data))
    return error, _convert_list_cbyte_to_list(c_data) #c_data _cbyte_list_to_list(c_data, numRegs*2)

def LJM_WriteMultipleBytes(handle, unitID, regAddress, numRegs, aData):
    c_data = _convert_list_to_list_cbyte(aData)
    error = static_lib.LJM_WriteMultipleBytes(handle, unitID, regAddress, numRegs, ctypes.byref(c_data))
    return error
"""

########

#LJM_ERROR_RETURN LJM_AddressesToMBFB(int MaxBytesPerMBFB, int * aAddresses, int * aTypes, int * aWrites, int * aNumValues, double * aValues, int * NumFrames, unsigned char * aMBFBCommand);
def LJM_AddressesToMBFB(MaxBytesPerMBFB, aAddresses, aTypes, aWrites, aNumValues, aValues, NumFrames):
    c_addrs = _convert_list_to_ctype_list(aAddresses, ctypes.c_int)
    c_types = _convert_list_to_ctype_list(aTypes, ctypes.c_int)
    c_writes = _convert_list_to_ctype_list(aWrites, ctypes.c_int)
    c_num_vals = _convert_list_to_ctype_list(aNumValues, ctypes.c_int)
    c_vals = _convert_list_to_ctype_list(aValues, ctypes.c_double)
    c_num_frames = ctypes.c_int(NumFrames)
    c_comm = (ctypes.c_ubyte*MaxBytesPerMBFB)(0)
    error = static_lib.LJM_AddressesToMBFB(MaxBytesPerMBFB, ctypes.byref(c_addrs), ctypes.byref(c_types), ctypes.byref(c_writes), ctypes.byref(c_num_vals), ctypes.byref(c_vals), ctypes.byref(c_num_frames), ctypes.byref(c_comm))
    if error != LJME_NOERROR:
        raise LJMError(error)
    return [c_num_frames.value, _convert_ctype_list_to_list(c_comm)]
    
#LJM_ERROR_RETURN LJM_NamesToAddresses(int NumFrames, const char ** NamesIn, int * aAddressesOut, int * aTypesOut);
def LJM_NamesToAddresses(NumFrames, NamesIn):
    c_names_in = _convert_string_list_to_ctype_list(NamesIn)
    c_addrs_out = (ctypes.c_int*NumFrames)(0)
    c_types_out = (ctypes.c_int*NumFrames)(0)
    error = static_lib.LJM_NamesToAddresses(NumFrames, ctypes.byref(c_names_in), ctypes.byref(c_addrs_out), ctypes.byref(c_types_out))
    if error != LJME_NOERROR:
        raise LJMError(error)
    return [c_addrs_out.value, c_types_out.value]

#LJM_ERROR_RETURN LJM_NameToAddress(const char * NameIn, int * AddressOut, int * TypeOut);
def LJM_NameToAddress(NameIn):
    c_addr_out = ctypes.c_int(0)
    c_type_out = ctypes.c_int(0)
    error = static_lib.LJM_NameToAddress(NameIn, ctypes.byref(c_addr_out), ctypes.byref(c_type_out))
    if error != LJME_NOERROR:
        raise LJMError(error)
    return [c_addr_out.value, c_type_out]

#parameter will change location
##LJM_ERROR_RETURN LJM_UpdateValues(unsigned char * aMBFBResponse, int * aTypes, int * aWrites, int * aNumValues, int NumFrames, double * aValues);


#test
#LJM_ERROR_RETURN LJM_MBFBComm(int Handle, unsigned char UnitID, unsigned char * aMBFB, int * errorFrame);
def LJM_MBFBComm(Handle, UnitID, aMBFB):
    c_mbfb = _convert_list_to_ctype_list(aMBFB, ctypes.c_ubyte)
    c_err_f = ctypes.c_int(0)
    error = static_lib.LJM_MBFBComm(Handle, UnitID, ctypes.byref(c_mbfb), ctypes.byref(c_err_f))
    if error != LJME_NOERROR:
        raise LJMError(error, c_err_f.value)
    return _convert_ctype_list_to_list(c_mbfb)

#LJM_VOID_RETURN LJM_SetSendReceiveTimeout(unsigned int TimeoutMS);
def LJM_SetSendReceiveTimeout(TimeoutMS):
    static_lib.LJM_SetSendReceiveTimeout(TimeoutMS)

#LJM_VOID_RETURN LJM_SetOpenTCPDeviceTimeout(unsigned int TimeoutSec, unsigned int TimeoutUSec);
def LJM_SetOpenTCPDeviceTimeout(TimeoutSec, TimeoutUSec):
    static_lib.LJM_SetOpenTCPDeviceTimeout(TimeoutSec, TimeoutUSec)

#LJM_ERROR_RETURN LJM_OpenFirstFound(int * DeviceType, int * ConnectionType, int * Handle);
''' deprecated ?
def LJM_OpenFirstFound():
    c_dev = ctypes.c_int()
    c_conn = ctypes.c_int()
    c_handle = ctypes.c_int()
    error = static_lib.LJM_OpenFirstFound(ctypes.byref(c_dev), ctypes.byref(c_conn), ctypes.byref(c_handle))
    return error, c_dev.value, c_conn.value, c_handle.value
'''

#LJM_ERROR_RETURN LJM_OpenS(const char * DeviceType, const char * ConnectionType, const char * Identifier, int * Handle);
def LJM_OpenS(DeviceType, ConnectionType, Identifier):
    c_handle = ctypes.c_int(0)
    #test if need byref (not sure if a output string is returned) 
    error = static_lib.LJM_OpenS(DeviceType, ConnectionType, Identifier, ctypes.byref(c_handle))
    if error != LJME_NOERROR:
        raise LJMError(error)
    return c_handle.value

#def LJM_ERROR_RETURN LJM_Open(int * DeviceType, int * ConnectionType, const char * Identifier, int * Handle);
def LJM_Open(DeviceType, ConnectionType, Identifier):
    c_dev = ctypes.c_int(DeviceType)
    c_conn = ctypes.c_int(ConnectionType)
    c_handle = ctypes.c_int(0)
    error = static_lib.LJM_Open(ctypes.byref(c_dev), ctypes.byref(c_conn), Identifier, ctypes.byref(c_handle))
    if error != LJME_NOERROR:
        raise LJMError(error)
    return [c_dev.value, c_conn.value, c_handle.value]

#LJM_ERROR_RETURN LJM_GetHandleInfo(int Handle, int * DeviceType, int * ConnectionType, int * SerialNumber, int * IPAddress, int * Port, int * PacketMaxBytes);
def LJM_GetHandleInfo(Handle):
    c_dev = ctypes.c_int(0)
    c_conn = ctypes.c_int(0)
    c_ser = ctypes.c_int(0)
    c_ip_addr = ctypes.c_int(0)
    c_port = ctypes.c_int(0)
    c_pkt_max = ctypes.c_int(0)
    error = static_lib.LJM_GetHandleInfo(Handle, ctypes.byref(c_dev), ctypes.byref(c_conn), ctypes.byref(c_ser), ctypes.byref(c_ip_addr), ctypes.byref(c_port), ctypes.byref(c_pkt_max))
    if error != LJME_NOERROR:
        raise LJMError(error)
    return [c_dev.value, c_conn.value, c_ser.value, c_ip_addr.value, c_port.value, c_pkt_max.value]

#LJM_ERROR_STRING LJM_ErrorToString(int ErrorCode);
def LJM_ErrorToString(ErrorCode):
    return ctypes.c_char_p(static_lib.LJM_ErrorToString(ErrorCode)).value

#LJM_VOID_RETURN LJM_LoadConstants();
def LJM_LoadConstants():
    static_lib.LJM_LoadConstants()

#LJM_ERROR_RETURN LJM_Close(int Handle)
def LJM_Close(Handle):
    error = static_lib.LJM_Close(Handle)
    if error != LJME_NOERROR:
        raise LJMError(error)

#LJM_ERROR_RETURN LJM_CloseAll();
def LJM_CloseAll():
    error = static_lib.LJM_CloseAll()
    if error != LJME_NOERROR:
        raise LJMError(error)

#LJM_ERROR_RETURN LJM_WriteRaw(int Handle, unsigned char * Data, int NumBytes);
def LJM_WriteRaw(Handle, Data, NumBytes):
    c_data = _convert_list_to_ctype_list(Data, ctypes.c_ubyte)
    error = static_lib.LJM_WriteRaw(Handle, ctypes.byref(c_data), NumBytes)
    if error != LJME_NOERROR:
        raise LJMError(error)

#LJM_ERROR_RETURN LJM_ReadRaw(int Handle, unsigned char * Data, int NumBytes);
def LJM_ReadRaw(Handle, NumBytes):
    c_data = (ctypes.c_ubyte*NumBytes)(0)
    error = static_lib.LJM_ReadRaw(Handle, ctypes.byref(c_data), NumBytes)
    if error != LJME_NOERROR:
        raise LJMError(error)
    return _convert_ctype_list_to_list(c_data)

#LJM_ERROR_RETURN LJM_eWriteAddress(int Handle, int Address, int Type, double Value);
def LJM_eWriteAddress(Handle, Address, Type, Value):
    error = static_lib.LJM_eWriteAddress(Handle, Address, Type, ctypes.c_double(Value))
    if error != LJME_NOERROR:
        raise LJMError(error)

#LJM_ERROR_RETURN LJM_eReadAddress(int Handle, int Address, int Type, double * Value);
def LJM_eReadAddress(Handle, Address, Type):
    c_val = ctypes.c_double(0)
    error = static_lib.LJM_eReadAddress(Handle, Address, Type, ctypes.byref(c_val))
    if error != LJME_NOERROR:
        raise LJMError(error)
    return c_val.value

#LJM_ERROR_RETURN LJM_eWriteName(int Handle, const char * Name, double Value);
def LJM_eWriteName(Handle, Name, Value):
    error = static_lib.LJM_eWriteName(Handle, Name, ctypes.c_double(Value))
    if error != LJME_NOERROR:
        raise LJMError(error)

#LJM_ERROR_RETURN LJM_eReadName(int Handle, const char * Name, double * Value);
def LJM_eReadName(Handle, Name):
    c_val = ctypes.c_double(0)
    error = static_lib.LJM_eReadName(Handle, Name, ctypes.byref(c_val))
    if error != LJME_NOERROR:
        raise LJMError(error)
    return c_val.value

#LJM_ERROR_RETURN LJM_eReadAddresses(int Handle, int NumFrames, int * aAddresses, int * aTypes, double * aValues, int * ErrorFrame);
def LJM_eReadAddresses(Handle, NumFrames, aAddresses, aTypes):
    c_addrs = _convert_list_to_ctype_list(aAddresses, ctypes.c_int)
    c_types = _convert_list_to_ctype_list(aTypes, ctypes.c_int)
    c_vals = (ctypes.c_double*NumFrames)(0)
    c_err_f = ctypes.c_int(0)
    error = static_lib.LJM_eReadAddresses(Handle, NumFrames, ctypes.byref(c_addrs), ctypes.byref(c_types), ctypes.byref(c_vals), ctypes.byref(c_err_f))
    if error != LJME_NOERROR:
        raise LJMError(error, c_err_f.value)
    return _convert_ctype_list_to_list(c_vals)

#LJM_ERROR_RETURN LJM_eWriteAddresses(int Handle, int NumFrames, int * aAddresses, int * aTypes, double * aValues, int * ErrorFrame);
def LJM_eWriteAddresses(Handle, NumFrames, aAddresses, aTypes, aValues):
    c_addrs = _convert_list_to_ctype_list(aAddresses, ctypes.c_int)
    c_types = _convert_list_to_ctype_list(aTypes, ctypes.c_int)
    c_vals =  _convert_list_to_ctype_list(aValues, ctypes.c_double)
    c_err_f = ctypes.c_int(0)
    error = static_lib.LJM_eWriteAddresses(Handle, NumFrames, ctypes.byref(c_addrs), ctypes.byref(c_types), ctypes.byref(c_vals), ctypes.byref(c_err_f))
    if error != LJME_NOERROR:
        raise LJMError(error, c_err_f.value)

#LJM_ERROR_RETURN LJM_eReadNames(int Handle, int NumFrames, const char ** Names, double * aValues, int * ErrorFrame);
def LJM_eReadNames(Handle, NumFrames, Names):
    c_names = _convert_string_list_to_ctype_list(Names)
    c_vals =  (ctypes.c_double*NumFrames)(0)
    c_err_f = ctypes.c_int(0)
    error = static_lib.LJM_eReadNames(Handle, NumFrames, ctypes.byref(c_names), ctypes.byref(c_vals), ctypes.byref(c_err_f))
    if error != LJME_NOERROR:
        raise LJMError(error, c_err_f.value)
    return _convert_ctype_list_to_list(c_vals)

#LJM_ERROR_RETURN LJM_eWriteNames(int Handle, int NumFrames, const char ** Names, double * aValues, int * ErrorFrame);
def LJM_eWriteNames(Handle, NumFrames, Names, aValues):
    c_names = _convert_string_list_to_ctype_list(Names)
    c_vals =  _convert_list_to_ctype_list(aValues, ctypes.c_double)
    c_err_f = ctypes.c_int(0)
    error = static_lib.LJM_eWriteNames(Handle, NumFrames, ctypes.byref(c_names), ctypes.byref(c_vals), ctypes.byref(c_err_f))
    if error != LJME_NOERROR:
        raise LJMError(error, c_err_f.value)

#LJM_ERROR_RETURN LJM_eAddresses(int Handle, int NumFrames, int * aAddresses, int * aTypes, int * aWrites, int * aNumValues, double * aValues, int * ErrorFrame);
def LJM_eAddresses(Handle, NumFrames, aAddresses, aTypes, aWrites, aNumValues, aValues):
    c_addrs = _convert_list_to_ctype_list(aAddresses, ctypes.c_int)
    c_types = _convert_list_to_ctype_list(aTypes, ctypes.c_int)
    c_writes = _convert_list_to_ctype_list(aWrites, ctypes.c_int)
    c_num_vals = _convert_list_to_ctype_list(aNumValues, ctypes.c_int)
    c_vals =  _convert_list_to_ctype_list(aValues, ctypes.c_double)
    c_err_f = ctypes.c_int(0)
    error = static_lib.LJM_eAddresses(Handle, NumFrames, ctypes.byref(c_addrs), ctypes.byref(c_types), ctypes.byref(c_writes), ctypes.byref(c_num_vals), ctypes.byref(c_vals), ctypes.byref(c_err_f))
    if error != LJME_NOERROR:
        raise LJMError(error, c_err_f.value)
    return _convert_ctype_list_to_list(c_vals)
    
#LJM_ERROR_RETURN LJM_eNames(int Handle, int NumFrames, const char ** Names, int * aWrites, int * aNumValues, double * aValues, int * ErrorFrame);
def LJM_eNames(Handle, NumFrames, Names, aWrites, aNumValues, aValues):
    c_names = _convert_string_list_to_ctype_list(Names)
    c_writes = _convert_list_to_ctype_list(aWrites, ctypes.c_int)
    c_num_vals = _convert_list_to_ctype_list(aNumValues, ctypes.c_int)
    c_vals =  _convert_list_to_ctype_list(aValues, ctypes.c_double)
    c_err_f = ctypes.c_int(0)
    error = static_lib.LJM_eNames(Handle, NumFrames, ctypes.byref(c_names), ctypes.byref(c_writes), ctypes.byref(c_num_vals), ctypes.byref(c_vals), ctypes.byref(c_err_f))
    if error != LJME_NOERROR:
        raise LJMError(error, c_err_f.value)
    return _convert_ctype_list_to_list(c_vals)
    
''' #removed?
#LJM_ERROR_RETURN LJM_WriteMultipleRegisters(int Handle, int RegAddress, int NumRegs, unsigned char * Data);
def LJM_WriteMultipleRegisters(Handle, RegAddress, NumRegs, Data):
    c_data = _convert_list_to_ctype_list(Data, ctypes.c_ubyte)
    error = static_lib.LJM_WriteMultipleRegisters(Handle, RegAddress, NumRegs, ctypes.byref(c_data))
    return error

#LJM_ERROR_RETURN LJM_ReadMultipleRegisters(int Handle, int RegAddress, int NumRegs, unsigned char * Data);
def LJM_ReadMultipleRegisters(Handle, RegAddress, NumRegs):
    c_data = (ctypes.c_ubyte*(NumRegs*2))(0)
    error = static_lib.LJM_ReadMultipleRegisters(Handle, RegAddress, NumRegs, ctypes.byref(c_data))
    return error, _convert_ctype_list_to_list(c_data)
'''

# Type conversion *

#LJM_VOID_RETURN LJM_FLOAT32ToByteArray(const float * aFLOAT32, int RegisterOffset, int NumFLOAT32, unsigned char * aBytes);
def LJM_FLOAT32ToByteArray(aFLOAT32, RegisterOffset, NumFLOAT32, aBytes):
    c_floats = _convert_list_to_ctype_list(aFLOAT32, ctypes.c_float)
    c_ubytes = _convert_list_to_ctype_list(aBytes, ctypes.c_ubyte)
    static_lib.LJM_FLOAT32ToByteArray(ctypes.byref(c_floats), RegisterOffset, NumFLOAT32, ctypes.byref(c_ubytes))
    return _convert_ctype_list_to_list(c_ubytes)
    
#LJM_VOID_RETURN LJM_ByteArrayToFLOAT32(const unsigned char * aBytes, int RegisterOffset, int NumFLOAT32, float * aFLOAT32);
def LJM_ByteArrayToFLOAT32(aBytes, RegisterOffset, NumFLOAT32, aFLOAT32):
    c_ubytes = _convert_list_to_ctype_list(aBytes, ctypes.c_ubyte)
    c_floats = _convert_list_to_ctype_list(aFLOAT32, ctypes.c_float)
    static_lib.LJM_ByteArrayToFLOAT32(ctypes.byref(c_ubytes), RegisterOffset, NumFLOAT32, ctypes.byref(c_floats))
    return _convert_ctype_list_to_list(c_floats)
 
#LJM_VOID_RETURN LJM_UINT16ToByteArray(const unsigned short * aUINT16, int RegisterOffset, int NumUINT16, unsigned char * aBytes);
def LJM_UINT16ToByteArray(aUINT16, RegisterOffset, NumUINT16, aBytes):
    c_uint16 = _convert_list_to_ctype_list(aUINT16, ctypes.c_uint16)
    c_ubytes = _convert_list_to_ctype_list(aBytes, ctypes.c_ubyte)
    static_lib.LJM_UINT16ToByteArray(ctypes.byref(c_uint16), RegisterOffset, NumUINT16, ctypes.byref(c_ubytes))
    return _convert_ctype_list_to_list(c_ubytes)
 
#LJM_VOID_RETURN LJM_ByteArrayToUINT16(const unsigned char * aBytes, int RegisterOffset, int NumUINT16, unsigned short * aUINT16);
def LJM_ByteArrayToUINT16(aBytes, RegisterOffset, NumUINT16, aUINT16):
    c_ubytes = _convert_list_to_ctype_list(aBytes, ctypes.c_ubyte)
    c_uint16 = _convert_list_to_ctype_list(aUINT16, ctypes.c_uint16)
    static_lib.LJM_ByteArrayToUINT16(ctypes.byref(c_ubytes), RegisterOffset, NumUINT16, ctypes.byref(c_uint16))
    return _convert_ctype_list_to_list(c_uint16)

#LJM_VOID_RETURN LJM_UINT32ToByteArray(const unsigned int * aUINT32, int RegisterOffset, int NumUINT32, unsigned char * aBytes);
def LJM_UINT32ToByteArray(aUINT32, RegisterOffset, NumUINT32, aBytes):
    c_uint32 = _convert_list_to_ctype_list(aUINT32, ctypes.c_uint32)
    c_ubytes = _convert_list_to_ctype_list(aBytes, ctypes.c_ubyte)
    static_lib.LJM_UINT32ToByteArray(ctypes.byref(c_uint32), RegisterOffset, NumUINT32, ctypes.byref(c_ubytes))
    return _convert_ctype_list_to_list(c_ubytes)
    
#LJM_VOID_RETURN LJM_ByteArrayToUINT32(const unsigned char * aBytes, int RegisterOffset, int NumUINT32, unsigned int * aUINT32);
def LJM_ByteArrayToUINT32(aBytes, RegisterOffset, NumUINT32, aUINT32):
    c_ubytes = _convert_list_to_ctype_list(aBytes, ctypes.c_ubyte)
    c_uint32 = _convert_list_to_ctype_list(aUINT32, ctypes.c_uint32)
    static_lib.LJM_UINT32ToByteArray(ctypes.byref(c_ubytes), RegisterOffset, NumUINT32, ctypes.byref(c_uint32))
    return _convert_ctype_list_to_list(c_uint32)

#LJM_VOID_RETURN LJM_INT32ToByteArray(const int * aINT32, int RegisterOffset, int NumINT32, unsigned char * aBytes);
def LJM_INT32ToByteArray(aINT32, RegisterOffset, NumINT32, aBytes):
    c_int32 = _convert_list_to_ctype_list(aINT32, ctypes.c_int32)
    c_ubytes = _convert_list_to_ctype_list(aBytes, ctypes.c_ubyte)
    static_lib.LJM_UINT32ToByteArray(ctypes.byref(c_int32), RegisterOffset, NumINT32, ctypes.byref(c_ubytes))
    return _convert_ctype_list_to_list(c_ubytes)

#LJM_VOID_RETURN LJM_ByteArrayToINT32(const unsigned char * aBytes, int RegisterOffset, int NumINT32, int * aINT32);
def LJM_ByteArrayToINT32(aBytes, RegisterOffset, NumINT32, aINT32):
    c_ubytes = _convert_list_to_ctype_list(aBytes, ctypes.c_ubyte)
    c_int32 = _convert_list_to_ctype_list(aINT32, ctypes.c_int32)
    static_lib.LJM_UINT32ToByteArray(ctypes.byref(c_ubytes), RegisterOffset, NumINT32, ctypes.byref(c_int32))
    return _convert_ctype_list_to_list(c_int32)

#LJM_DOUBLE_RETURN LJM_GetDriverVersion();
def LJM_GetDriverVersion():
    static_lib.LJM_GetDriverVersion.restype = ctypes.c_double
    return static_lib.LJM_GetDriverVersion()

## Functions end

## Constants
'''
# Device Types:
LJ_dtUE9 = 9
LJ_dtU3 = 3
LJ_dtU6 = 6
LJ_dtSMB = 1000

# Connection Types:
LJ_ctUSB = 1 # UE9 + U3 + U6
LJ_ctETHERNET = 2 # UE9 only
LJ_ctETHERNET_MB = 3 # Modbus over Ethernet, UE9 only.
LJ_ctETHERNET_DATA_ONLY = 4 # Opens data port but not stream port, UE9 only

LJ_ecDISCONNECT = 1
LJ_ecRECONNECT = 2 

# Raw connection types are used to open a device but not communicate with it
# should only be used if the normal connection types fail and for testing.
# If a device is opened with the raw connection types, only LJ_ioRAW_OUT
# and LJ_ioRAW_IN io types should be used
LJ_ctUSB_RAW = 101 # UE9 + U3 + U6
LJ_ctETHERNET_RAW = 102 # UE9 only

# Errorcodes:
LJE_NOERROR = 0

LJE_UNKNOWN_ERROR = 1001 # occurs when an unknown error occurs that is caught, but still unknown.
LJE_INVALID_HANDLE = 1003 # occurs when invalid handle used
LJE_LABJACK_NOT_FOUND = 1007 # occurs when the LabJack is not found at the given id or address
LJE_COMM_FAILURE = 1008 # occurs when unable to send or receive the correct # of bytes
LJE_DEVICE_ALREADY_OPEN = 1010 # occurs when LabJack is already open via USB in another program or process
LJE_USB_DRIVER_NOT_FOUND = 1012

# Modbus
DIRECTION_READ = 1
DIRECTION_WRITE = 2
DIRECTION_BI = 3
MAX_TRANSACTION_ID = 65535
MAX_REGISTER = 4294967295
BYTES_PER_REGISTER = 2

NUM_READ_COMMAND_BYTES = 14
NUM_BASE_WRITE_COMMAND_BYTES = 15
NUM_BASE_READ_RESPONSE_BYTES = 9
NUM_WRITE_RESPONSE_BYTES = 12
NUM_REPORTED_READ_COMMAND_BYTES = 6
NUM_BASE_REPORTED_READ_COMMAND_BYTES = 7
NUM_BASE_REPORTED_READ_RESPONSE_BYTES = 3
NUM_REPORTED_WRITE_RESPONSE_BYTES = 6
NUM_BASE_ERROR_RESPONSE_SIZE = 8
'''

# Read/Write direction constants:
LJM_READ = 0
LJM_WRITE = 1

# Data types:
# Automatic endian conversion, if needed by the processor
LJM_UINT16 = 0 # C type of unsigned short
LJM_UINT32 = 1 # C type of unsigned int
LJM_INT32 = 2 # C type of int
LJM_FLOAT32 = 3 # C type of float

# Advanced users data type:
# Does not do any endianness conversion
LJM_BYTE = 99 # C type of unsigned char

# LJM_NamesToAddresses sets this when a register name is not found
LJM_INVALID_NAME_ADDRESS = -1 # 0xFFFFFFFF or 4294967295
LJM_MAX_NAME_SIZE = 256

LJM_NOT_ENOUGH_DATA_SPACE = 9999.99

# Device types:
LJM_dtANY = 0
LJM_dtUE9 = 9
LJM_dtU3 = 3
LJM_dtU6 = 6
LJM_dtT7 = 7
LJM_dtSKYMOTE_BRIDGE = 1000
LJM_dtDIGIT = 200

# Connection types:
LJM_ctANY = 0
LJM_ctUSB = 1 # UE9 + U3
LJM_ctTCP = 2 # UE9 only

# TCP/Ethernet constants:
LJM_NO_IP_ADDRESS = 0
LJM_NO_PORT = 0
LJM_DEFAULT_PORT = 502
# This becomes 255.255.255.255 when passed to inet_ntoa():
LJM_UNKNOWN_IP_ADDRESS = -1

# Identifier types:
LJM_DEMO_MODE = "-1"
LJM_idANY = 0

# LJM_AddressesToMBFB Constants
LJM_DEFAULT_FEEDBACK_ALLOCATION_SIZE = 62
LJM_USE_DEFAULT_MAXBYTESPERMBFB = 0

# Please note that some devices must append 2 bytes to certain packets. Please check the docs
# for the device you are using.
LJM_MAX_USB_PACKET_NUM_BYTES = 64
LJM_MAX_TCP_PACKET_NUM_BYTES_T7 = 1400 # Note that this will probably change
LJM_MAX_TCP_PACKETS_NUM_BYTES_NON_T7 = 64 # This may change

# Timeout Constants
LJM_NO_TIMEOUT = 0
LJM_DEFAULT_TIMEOUT = 1000

# Errorcodes

# Success
LJME_NOERROR = 0

# Warnings:
LJME_WARNINGS_BEGIN = 200
LJME_WARNINGS_END = 399
LJME_FRAMES_OMITTED_DUE_TO_PACKET_SIZE = 201

# Modbus Errors:
LJME_MODBUS_ERRORS_BEGIN = 1200
LJME_MODBUS_ERRORS_END = 1216
LJME_MBE1_ILLEGAL_FUNCTION = 1201
LJME_MBE2_ILLEGAL_DATA_ADDRESS = 1202
LJME_MBE3_ILLEGAL_DATA_VALUE = 1203
LJME_MBE4_SLAVE_DEVICE_FAILURE = 1204
LJME_MBE5_ACKNOWLEDGE = 1205
LJME_MBE6_SLAVE_DEVICE_BUSY = 1206
LJME_MBE8_MEMORY_PARITY_ERROR = 1208
LJME_MBE10_GATEWAY_PATH_UNAVAILABLE = 1210
LJME_MBE11_GATEWAY_TARGET_NO_RESPONSE = 1211

# Driver Errors:
LJME_DRIVER_ERRORS_BEGIN = 1220
LJME_DRIVER_ERRORS_END = 1399

LJME_UNKNOWN_ERROR = 1221
LJME_INVALID_DEVICE_TYPE = 1222
LJME_INVALID_HANDLE = 1223
LJME_DEVICE_NOT_OPEN = 1224
LJME_LABJACK_NOT_FOUND = 1227
LJME_DEVICE_ALREADY_OPEN = 1230
LJME_CANNOT_CONNECT = 1231
LJME_CANNOT_CREATE_SOCKET = 1232
LJME_SETSOCKOPT_ERROR = 1233
LJME_SENDTO_ERROR = 1234
LJME_SELECT_ERROR = 1235
LJME_CANNOT_OPEN_DEVICE = 1236
LJME_CANNOT_DISCONNECT = 1237
LJME_WINSOCK_FAILURE = 1238
LJME_DEVICE_RECONNECT_FAILED = 1239
LJME_INVALID_FUNCTION_CODE_RETURNED = 1240
LJME_TRANSACTION_ID_MISMATCH =  1241
LJME_UNIT_ID_MISMATCH = 1242

LJME_INVALID_ADDRESS = 1250
LJME_INVALID_CONNECTION_TYPE = 1251
LJME_INVALID_DIRECTION = 1252
LJME_INVALID_FUNCTION = 1253

LJME_INVALID_NUM_REGISTERS = 1254
LJME_INVALID_PARAMETER = 1255
LJME_INVALID_PROTOCOL_ID = 1256
LJME_INVALID_TRANSACTION_ID = 1257
LJME_INVALID_UNIT_ID = 1258
LJME_INVALID_VALUE_TYPE = 1259
LJME_MEMORY_ALLOCATION_FAILURE = 1260

LJME_NO_COMMAND_BYTES_SENT = 1261

LJME_INCORRECT_NUM_COMMAND_BYTES_SENT = 1262

LJME_NO_RESPONSE_BYTES_RECEIVED = 1263

LJME_INCORRECT_NUM_RESPONSE_BYTES_RECEIVED = 1264

LJME_MIXED_FORMAT_IP_ADDRESS = 1265

LJME_UNKNOWN_IDENTIFIER = 1266
LJME_NOT_IMPLEMENTED = 1267
LJME_INVALID_INDEX = 1268

LJME_INVALID_LENGTH = 1269
LJME_ERROR_BIT_SET = 1270

LJME_INVALID_MAXBYTESPERMBFB = 1271

LJME_NULL_POINTER = 1272

LJME_NULL_OBJ = 1273

LJME_RESERVED_NAME = 1274

LJME_UNPARSABLE_DEVICE_TYPE = 1275

LJME_UNPARSABLE_CONNECTION_TYPE = 1276

LJME_UNPARSABLE_IDENTIFIER = 1277

LJME_PACKET_SIZE_TOO_LARGE = 1278

LJME_TRANSACTION_ID_ERR = 1279
LJME_PROTOCOL_ID_ERR = 1280
LJME_LENGTH_ERR = 1281
LJME_UNIT_ID_ERR = 1282
LJME_FUNCTION_ERR = 1283
LJME_STARTING_REG_ERR = 1284
LJME_NUM_REGS_ERR = 1285
LJME_NUM_BYTES_ERR = 1286
LJME_READ_DATA_ERR = 1287
LJME_WRITE_DATA_ERR = 1288
LJME_READ_VALIDATION_ERR = 1289
LJME_FRAME_FUNCTION_ERR = 1290
LJME_INVALID_NUM_VALUES = 1291
LJME_MODBUS_CONSTANTS_FILE_NOT_FOUND = 1292
LJME_INVALID_MODBUS_CONSTANTS_FILE = 1293
LJME_INVALID_NAME_LIST = 1294
LJME_OVERSPECIFIED_IDENTIFIER = 1295
LJME_OVERSPECIFIED_PORT = 1296
## Constants end

### Wrapper functions for LJModbus library end