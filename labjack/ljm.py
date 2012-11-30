"""
Python wrapper for the LJM driver.

"""
import ctypes
import os
import struct

__version__ = "0.1.0"

## LJM Exception
class LJMError(Exception):
    """
    Custom Exception meant for dealing with LJM specific errors
    """
    def __init__(self, errorCode = None, errorFrame = None, errorString = ""):
        self._errorCode = errorCode
        if errorCode is LJME_NOERROR or errorCode is None:
            self._isWarning = False
        else:
            self._isWarning = _isWarningErrorCode(errorCode)
        self._errorFrame = errorFrame
        self._errorString = str(errorString)
        if not self._errorString:
            try:
                self._errorString = errorToString(errorCode)  
            except:
                pass

    @property
    def errorCode(self):
        return self._errorCode

    @property
    def errorFrame(self):
        return self._errorFrame

    @property
    def errorString(self):
        return self._errorString

    @property
    def isWarning(self):
        return self._isWarning
    
    def __str__(self):
        frameStr = ""
        errorCodeStr = ""
        errorStr = ""
        if self._errorFrame is not None:
            frameStr = "Frame " + str(self._errorFrame) + " "
        if self._errorCode is not None:
            errorCodeStr = " (" + str(self._errorCode) + ")"
        if self._isWarning:
            errorStr = "Warning" + errorCodeStr + " "
        else:
            errorStr = "Error" + errorCodeStr + " "  + self._errorString
        return frameStr + errorStr
## LJM Exception end

### Load LJM library
def _loadLibrary():
    """
    _loadLibrary()
    Returns a ctypes pointer to the library.
    """
    try:
        if(os.name == "posix"):
            try:
                #Linux
                return ctypes.CDLL("libLabJackM.so")
            except OSError, e:
                pass # May be on Mac.
            except Exception, e:
                raise LJMError(errorString = ("Cannot load the LJM Linux SO.  " + str(e)))
            
            try:
                return ctypes.CDLL("libLabJackM.dylib")
            except OSError, e:
                raise LJMError(errorString = ("Cannot load the LJM driver.  Check that the driver is installed.  " + str(e)))
            except Exception, e:
                raise LJMError(errorString = ("Cannot load the LJM Mac OS X Dylib.  " + str(e)))
        if(os.name == "nt"):
            #Windows
            try:
                #Win
                return ctypes.CDLL("LabJackM.dll")
            except Exception, e:
                raise LJMError(errorString = ("Cannot load LJM driver.  " + str(e)))
    except LJMError, e:
        print str(type(e)) + ": " + str(e)
        return None

_staticLib = _loadLibrary()
### Load LJM library end

### Classes

## Device
class Device(object):
    """
    Device class that represents a LabJack device.
    """
    #may not be able to default deviceType and connectionType
    def __init__(self, deviceType=0, connectionType=0, identifier="LJM_idANY", debug=False, autoOpen=True):
        self._handle = None
        self.deviceType = None
        self.connectionType = None
        self.serialNumber = None
        self.ipAddress = None
        self.port = None
        self.maxBytesPerMB = None
        if autoOpen:
            if isinstance(deviceType, str) and isinstance(connectionType, str):
                self.openS(deviceType, connectionType, str(identifier))
            elif str(deviceType).isdigit() and str(connectionType).isdigit():
                self.open(int(deviceType), int(connectionType), str(identifier))
            else:
                raise LJMError(errorString = "device and connection types are not both strings or integers")
    
    def __del__(self):
        pass

    def openS(self, deviceType="LJM_dtANY", connectionType="LJM_ctANY", identifier="LJM_idANY"):
        self._handle = openS(deviceType, connectionType, identifier)
        if len(self._handle) > 1:
            #There was a warning
            self._handle = self._handle[0]
        self.getHandleInfo()

    def open(self, deviceType=0, connectionType=0, identifier="LJM_idANY"):
        self._handle = open(deviceType, connectionType, identifier)[2]
        self.getHandleInfo()

    def close(self):
        close(self._handle)

    def addressesToMBFB(self, maxBytesPerMBFB, aAddresses, aDataTypes, aWrites, aNumValues, aValues, numFrames):
        return addressesToMBFB(maxBytesPerMBFB, aAddresses, aDataTypes, aWrites, aNumValues, aValues, numFrames)

    def MBFBComm(self, unitID, aMBFB):
        return MBFBComm(self._handle, unitID, aMBFB)
    
    def updateValues(self, aMBFBResponse, aDataTypes, aWrites, aNumValues, numFrames):
        return updateValues(aMBFBResponse, aDataTypes, aWrites, aNumValues, numFrames)

    def namesToAddresses(self, numFrames, namesIn):
        return namesToAddresses(numFrames, namesIn)

    def nameToAddress(self, nameIn):
        return nameToAddress(nameIn)

    def getHandleInfo(self):
        info = getHandleInfo(self._handle)
        self.deviceType = info[0]
        self.connectionType = info[1]
        self.serialNumber = info[2]
        self.ipAddress = info[3]
        self.port = info[4]
        self.maxBytesPerMB = info[5]
        return info

    def errorToString(self, errorCode):
        return errorToString(errorCode)
   
    def writeRaw(self, data, numBytes):
        writeRaw(self._handle, data, numBytes)

    def readRaw(self, numBytes):
        return readRaw(self._handle, numBytes)

    def eWriteAddress(self, address, dataType, value):
        eWriteAddress(self._handle, address, dataType, value)

    def eReadAddress(self, address, dataType):
        return eReadAddress(self._handle, address, dataType)

    def eWriteName(self, name, value):
        eWriteName(self._handle, name, value)

    def eReadName(self, name):
        return eReadName(self._handle, name)

    def eReadAddresses(self, numFrames, aAddresses, aDataTypes):
        return eReadAddresses(self._handle, numFrames, aAddresses, aDataTypes)

    def eWriteAddresses(self, numFrames, aAddresses, aDataTypes, aValues):
        eWriteAddresses(self._handle, numFrames, aAddresses, aDataTypes, aValues)

    def eReadNames(self, numFrames, names):
        return eReadNames(self._handle, numFrames, names)

    def eWriteNames(self, numFrames, names, aValues):
        eWriteNames(self._handle, numFrames, names, aValues)

    def eAddresses(self, numFrames, aAddresses, aDataTypes, aWrites, aNumValues, aValues):
        return eAddresses(self._handle, numFrames, aAddresses, aDataTypes, aWrites, aNumValues, aValues)

    def eNames(self, numFrames, names, aWrites, aNumValues, aValues):
        return eNames(self._handle, numFrames, names, aWrites, aNumValues, aValues)

    def FLOAT32ToByteArray(self, aFLOAT32, registerOffset, numFLOAT32, aBytes):
        return FLOAT32ToByteArray(aFLOAT32, registerOffset, numFLOAT32, aBytes)

    def byteArrayToFLOAT32(self, aBytes, registerOffset, numFLOAT32, aFLOAT32):
        return byteArrayToFLOAT32(aBytes, registerOffset, numFLOAT32, aFLOAT32)

    def UINT16ToByteArray(self, aUINT16, registerOffset, numUINT16, aBytes):
        return UINT16ToByteArray(aUINT16, registerOffset, numUINT16, aBytes)

    def byteArrayToUINT16(self, aBytes, registerOffset, numUINT16, aUINT16):
        return byteArrayToUINT16(aBytes, registerOffset, numUINT16, aUINT16)

    def UINT32ToByteArray(self, aUINT32, registerOffset, numUINT32, aBytes):
        return UINT32ToByteArray(aUINT32, registerOffset, numUINT32, aBytes)

    def byteArrayToUINT32(self, aBytes, registerOffset, numUINT32, aUINT32):
        return byteArrayToUINT32(aBytes, registerOffset, numUINT32, aUINT32)

    def INT32ToByteArray(self, aINT32, registerOffset, numINT32, aBytes):
        return INT32ToByteArray(aINT32, registerOffset, numINT32, aBytes)

    def byteArrayToINT32(self, aBytes, registerOffset, numINT32, aINT32):
        return byteArrayToINT32(aBytes, registerOffset, numINT32, aINT32)

## Device end

### Classes end

## Helper functions

def _convertListToCtypeList(li, cType):
    cList = (cType*len(li))(0)
    for i in range(len(li)):
        cList[i] = cType(li[i])
    return cList

def _convertCtypeListToList(listCtype):
    return [i for i in listCtype]

def _isWarningErrorCode(errorCode):
    if errorCode >= LJME_WARNINGS_BEGIN and errorCode <= LJME_WARNINGS_END:
        return True
    else:
        return False
## Private Helper functions end

### Wrapper for LJM library

## Functions

#LJM_DOUBLE_RETURN LJM_GetDriverVersion();
def getDriverVersion():
    _staticLib.LJM_GetDriverVersion.restype = ctypes.c_double
    return _staticLib.LJM_GetDriverVersion()

#LJM_VOID_RETURN LJM_SetSendReceiveTimeout(unsigned int TimeoutMS);
def setSendReceiveTimeout(timeoutMS):
    _staticLib.LJM_SetSendReceiveTimeout(timeoutMS)

#LJM_VOID_RETURN LJM_SetOpenTCPDeviceTimeout(unsigned int TimeoutSec, unsigned int TimeoutUSec);
def setOpenTCPDeviceTimeout(timeoutSec, timeoutUSec):
    _staticLib.LJM_SetOpenTCPDeviceTimeout(timeoutSec, timeoutUSec)

#LJM_ERROR_RETURN LJM_ListAll(int DeviceType, int ConnectionType, int * NumFound, int * aSerialNumbers, int * aIPAddresses);
def listAll(deviceType, connectionType):
    cNumFound = ctypes.c_int32(0)
    cSerNums = (ctypes.c_int32*LJM_LIST_ALL_SIZE)(0)
    cIPAddrs = (ctypes.c_int32*LJM_LIST_ALL_SIZE)(0)
    error = _staticLib.LJM_ListAll(deviceType, connectionType, ctypes.byref(cNumFound), ctypes.byref(cSerNums), ctypes.byref(cIPAddrs))
    if error != LJME_NOERROR:
        if _isWarningErrorCode(error):
            return cNumFound.value, _convertCtypeListToList(cSerNums[0:cNumFound.value]), _convertCtypeListToList(cIPAddrs[0:cNumFound.value]), error
        else:
            raise LJMError(error)
    return cNumFound.value, _convertCtypeListToList(cSerNums[0:cNumFound.value]), _convertCtypeListToList(cIPAddrs[0:cNumFound.value])

#LJM_ERROR_RETURN LJM_ListAllS(const char * DeviceType, const char * ConnectionType, int * NumFound, int * aSerialNumbers, int * aIPAddresses);
def listAllS(deviceType, connectionType):
    cNumFound = ctypes.c_int32(0)
    cSerNums = (ctypes.c_int32*LJM_LIST_ALL_SIZE)(0)
    cIPAddrs = (ctypes.c_int32*LJM_LIST_ALL_SIZE)(0)
    error = _staticLib.LJM_ListAllS(deviceType, connectionType, ctypes.byref(cNumFound), ctypes.byref(cSerNums), ctypes.byref(cIPAddrs))
    if error != LJME_NOERROR:
        if _isWarningErrorCode(error):
            return cNumFound.value, _convertCtypeListToList(cSerNums[0:cNumFound.value]), _convertCtypeListToList(cIPAddrs[0:cNumFound.value]), error
        else:
            raise LJMError(error)
    return cNumFound.value, _convertCtypeListToList(cSerNums[0:cNumFound.value]), _convertCtypeListToList(cIPAddrs[0:cNumFound.value])

#LJM_VOID_RETURN LJM_LoadConstants();
def loadConstants():
    _staticLib.LJM_LoadConstants()

#LJM_ERROR_RETURN LJM_CloseAll();
def closeAll():
    error = _staticLib.LJM_CloseAll()
    if error != LJME_NOERROR:
        raise LJMError(error)


#LJM_ERROR_RETURN LJM_AddressesToMBFB(int MaxBytesPerMBFB, int * aAddresses, int * aTypes, int * aWrites, int * aNumValues, double * aValues, int * NumFrames, unsigned char * aMBFBCommand);
def addressesToMBFB(maxBytesPerMBFB, aAddresses, aDataTypes, aWrites, aNumValues, aValues, numFrames):
    cAddrs = _convertListToCtypeList(aAddresses, ctypes.c_int32)
    cTypes = _convertListToCtypeList(aDataTypes, ctypes.c_int32)
    cWrites = _convertListToCtypeList(aWrites, ctypes.c_int32)
    cNumVals = _convertListToCtypeList(aNumValues, ctypes.c_int32)
    cVals = _convertListToCtypeList(aValues, ctypes.c_double)
    cNumFrames = ctypes.c_int32(numFrames)
    cComm = (ctypes.c_ubyte*maxBytesPerMBFB)(0)
    error = _staticLib.LJM_AddressesToMBFB(maxBytesPerMBFB, ctypes.byref(cAddrs), ctypes.byref(cTypes), ctypes.byref(cWrites), ctypes.byref(cNumVals), ctypes.byref(cVals), ctypes.byref(cNumFrames), ctypes.byref(cComm))
    if error != LJME_NOERROR:
        if _isWarningErrorCode(error):
            return cNumFrames.value, _convertCtypeListToList(cComm), error
        else:
            raise LJMError(error)
    return cNumFrames.value, _convertCtypeListToList(cComm)

#LJM_ERROR_RETURN LJM_MBFBComm(int Handle, unsigned char UnitID, unsigned char * aMBFB, int * errorFrame);
def MBFBComm(handle, unitID, aMBFB):
    cMBFB = _convertListToCtypeList(aMBFB, ctypes.c_ubyte)
    cErrorFrame = ctypes.c_int32(0)
    error = _staticLib.LJM_MBFBComm(handle, unitID, ctypes.byref(cMBFB), ctypes.byref(cErrorFrame))
    if error != LJME_NOERROR:
        raise LJMError(error, cErrorFrame.value)
    return _convertCtypeListToList(cMBFB)

#LJM_ERROR_RETURN LJM_UpdateValues(unsigned char * aMBFBResponse, int * aTypes, int * aWrites, int * aNumValues, int NumFrames, double * aValues);
def updateValues(aMBFBResponse, aDataTypes, aWrites, aNumValues, numFrames):
    cMBFB = _convertListToCtypeList(aMBFBResponse, ctypes.c_ubyte)
    cTypes = _convertListToCtypeList(aDataTypes, ctypes.c_int32)
    cWrites = _convertListToCtypeList(aWrites, ctypes.c_int32)
    cNumVals = _convertListToCtypeList(aNumValues, ctypes.c_int32)
    cVals = (ctypes.c_double*numFrames)(0)
    error = _staticLib.LJM_UpdateValues(ctypes.byref(cMBFB), ctypes.byref(cTypes), ctypes.byref(cWrites), ctypes.byref(cNumVals), numFrames, ctypes.byref(cVals))
    if error != LJME_NOERROR:
        raise LJMError(error)
    return _convertCtypeListToList(cVals)

#LJM_ERROR_RETURN LJM_NamesToAddresses(int NumFrames, const char ** NamesIn, int * aAddressesOut, int * aTypesOut);
def namesToAddresses(numFrames, namesIn):
    cNames = _convertListToCtypeList(namesIn, ctypes.c_char_p)
    cAddrsOut = (ctypes.c_int32*numFrames)(0)
    cTypesOut = (ctypes.c_int32*numFrames)(0)
    error = _staticLib.LJM_NamesToAddresses(numFrames, ctypes.byref(cNames), ctypes.byref(cAddrsOut), ctypes.byref(cTypesOut))
    if error != LJME_NOERROR:
        raise LJMError(error)
    return _convertCtypeListToList(cAddrsOut), _convertCtypeListToList(cTypesOut)

#LJM_ERROR_RETURN LJM_NameToAddress(const char * NameIn, int * AddressOut, int * TypeOut);
def nameToAddress(nameIn):
    cAddrOut = ctypes.c_int32(0)
    cTypeOut = ctypes.c_int32(0)
    error = _staticLib.LJM_NameToAddress(nameIn, ctypes.byref(cAddrOut), ctypes.byref(cTypeOut))
    if error != LJME_NOERROR:
        raise LJMError(error)
    return cAddrOut.value, cTypeOut.value

#LJM_ERROR_RETURN LJM_OpenS(const char * DeviceType, const char * ConnectionType, const char * Identifier, int * Handle);
def openS(deviceType, connectionType, identifier):
    cHandle = ctypes.c_int32(0)
    error = _staticLib.LJM_OpenS(deviceType, connectionType, identifier, ctypes.byref(cHandle))
    if error != LJME_NOERROR:
        if _isWarningErrorCode(error):
            return cHandle.value, error
        else:
            raise LJMError(error)
    return cHandle.value

#def LJM_ERROR_RETURN LJM_Open(int * DeviceType, int * ConnectionType, const char * Identifier, int * Handle);
def open(deviceType, connectionType, identifier):
    cDev = ctypes.c_int32(deviceType)
    cConn = ctypes.c_int32(connectionType)
    cHandle = ctypes.c_int32(0)
    error = _staticLib.LJM_Open(ctypes.byref(cDev), ctypes.byref(cConn), identifier, ctypes.byref(cHandle))
    if error != LJME_NOERROR:
        if _isWarningErrorCode(error):
            return cDev.value, cConn.value, cHandle.value, error
        else:
            raise LJMError(error)
    return cDev.value, cConn.value, cHandle.value

#LJM_ERROR_RETURN LJM_GetHandleInfo(int Handle, int * DeviceType, int * ConnectionType, int * SerialNumber, int * IPAddress, int * Port, int * PacketMaxBytes);
def getHandleInfo(handle):
    cDev = ctypes.c_int32(0)
    cConn = ctypes.c_int32(0)
    cSer = ctypes.c_int32(0)
    cIPAddr = ctypes.c_int32(0)
    cPort = ctypes.c_int32(0)
    cPktMax = ctypes.c_int32(0)
    error = _staticLib.LJM_GetHandleInfo(handle, ctypes.byref(cDev), ctypes.byref(cConn), ctypes.byref(cSer), ctypes.byref(cIPAddr), ctypes.byref(cPort), ctypes.byref(cPktMax))
    if error != LJME_NOERROR:
        raise LJMError(error)
    return cDev.value, cConn.value, cSer.value, cIPAddr.value, cPort.value, cPktMax.value

#LJM_ERROR_STRING LJM_ErrorToString(int ErrorCode);
def errorToString(errorCode):
    errStr = " " * LJM_MAX_NAME_SIZE
    _staticLib.LJM_ErrorToString(errorCode, errStr)
    return errStr.strip()

#LJM_ERROR_RETURN LJM_Close(int Handle)
def close(handle):
    error = _staticLib.LJM_Close(handle)
    if error != LJME_NOERROR:
        raise LJMError(error)

#LJM_ERROR_RETURN LJM_WriteRaw(int Handle, unsigned char * Data, int NumBytes);
def writeRaw(handle, data, numBytes):
    cData = _convertListToCtypeList(data, ctypes.c_ubyte)
    error = _staticLib.LJM_WriteRaw(handle, ctypes.byref(cData), numBytes)
    if error != LJME_NOERROR:
        raise LJMError(error)

#LJM_ERROR_RETURN LJM_ReadRaw(int Handle, unsigned char * Data, int NumBytes);
def readRaw(handle, numBytes):
    cData = (ctypes.c_ubyte*numBytes)(0)
    error = _staticLib.LJM_ReadRaw(handle, ctypes.byref(cData), numBytes)
    if error != LJME_NOERROR:
        raise LJMError(error)
    return _convertCtypeListToList(cData)

#LJM_ERROR_RETURN LJM_eWriteAddress(int Handle, int Address, int Type, double Value);
def eWriteAddress(handle, address, dataType, value):
    error = _staticLib.LJM_eWriteAddress(handle, address, dataType, ctypes.c_double(value))
    if error != LJME_NOERROR:
        raise LJMError(error)

#LJM_ERROR_RETURN LJM_eReadAddress(int Handle, int Address, int Type, double * Value);
def eReadAddress(handle, address, dataType):
    cVal = ctypes.c_double(0)
    error = _staticLib.LJM_eReadAddress(handle, address, dataType, ctypes.byref(cVal))
    if error != LJME_NOERROR:
        raise LJMError(error)
    return cVal.value

#LJM_ERROR_RETURN LJM_eWriteName(int Handle, const char * Name, double Value);
def eWriteName(handle, name, value):
    error = _staticLib.LJM_eWriteName(handle, name, ctypes.c_double(value))
    if error != LJME_NOERROR:
        raise LJMError(error)

#LJM_ERROR_RETURN LJM_eReadName(int Handle, const char * Name, double * Value);
def eReadName(handle, name):
    cVal = ctypes.c_double(0)
    error = _staticLib.LJM_eReadName(handle, name, ctypes.byref(cVal))
    if error != LJME_NOERROR:
        raise LJMError(error)
    return cVal.value

#LJM_ERROR_RETURN LJM_eReadAddresses(int Handle, int NumFrames, int * aAddresses, int * aTypes, double * aValues, int * ErrorFrame);
def eReadAddresses(handle, numFrames, aAddresses, aDataTypes):
    cAddrs = _convertListToCtypeList(aAddresses, ctypes.c_int32)
    cTypes = _convertListToCtypeList(aDataTypes, ctypes.c_int32)
    cVals = (ctypes.c_double*numFrames)(0)
    cErrorFrame = ctypes.c_int32(0)
    error = _staticLib.LJM_eReadAddresses(handle, numFrames, ctypes.byref(cAddrs), ctypes.byref(cTypes), ctypes.byref(cVals), ctypes.byref(cErrorFrame))
    if error != LJME_NOERROR:
        raise LJMError(error, cErrorFrame.value)
    return _convertCtypeListToList(cVals)

#LJM_ERROR_RETURN LJM_eWriteAddresses(int Handle, int NumFrames, int * aAddresses, int * aTypes, double * aValues, int * ErrorFrame);
def eWriteAddresses(handle, numFrames, aAddresses, aDataTypes, aValues):
    cAddrs = _convertListToCtypeList(aAddresses, ctypes.c_int32)
    cTypes = _convertListToCtypeList(aDataTypes, ctypes.c_int32)
    cVals =  _convertListToCtypeList(aValues, ctypes.c_double)
    cErrorFrame = ctypes.c_int32(0)
    error = _staticLib.LJM_eWriteAddresses(handle, numFrames, ctypes.byref(cAddrs), ctypes.byref(cTypes), ctypes.byref(cVals), ctypes.byref(cErrorFrame))
    if error != LJME_NOERROR:
        raise LJMError(error, cErrorFrame.value)

#LJM_ERROR_RETURN LJM_eReadNames(int Handle, int NumFrames, const char ** Names, double * aValues, int * ErrorFrame);
def eReadNames(handle, numFrames, names):
    cNames = _convertListToCtypeList(names, ctypes.c_char_p)
    cVals =  (ctypes.c_double*numFrames)(0)
    cErrorFrame = ctypes.c_int32(0)
    error = _staticLib.LJM_eReadNames(handle, numFrames, cNames, ctypes.byref(cVals), ctypes.byref(cErrorFrame))
    if error != LJME_NOERROR:
        raise LJMError(error, cErrorFrame.value)
    return _convertCtypeListToList(cVals)

#LJM_ERROR_RETURN LJM_eWriteNames(int Handle, int NumFrames, const char ** Names, double * aValues, int * ErrorFrame);
def eWriteNames(handle, numFrames, names, aValues):
    cNames = _convertListToCtypeList(names, ctypes.c_char_p)
    cVals =  _convertListToCtypeList(aValues, ctypes.c_double)
    cErrorFrame = ctypes.c_int32(0)
    error = _staticLib.LJM_eWriteNames(handle, numFrames, ctypes.byref(cNames), ctypes.byref(cVals), ctypes.byref(cErrorFrame))
    if error != LJME_NOERROR:
        raise LJMError(error, cErrorFrame.value)

#LJM_ERROR_RETURN LJM_eAddresses(int Handle, int NumFrames, int * aAddresses, int * aTypes, int * aWrites, int * aNumValues, double * aValues, int * ErrorFrame);
def eAddresses(handle, numFrames, aAddresses, aDataTypes, aWrites, aNumValues, aValues):
    cAddrs = _convertListToCtypeList(aAddresses, ctypes.c_int32)
    cTypes = _convertListToCtypeList(aDataTypes, ctypes.c_int32)
    cWrites = _convertListToCtypeList(aWrites, ctypes.c_int32)
    cNumVals = _convertListToCtypeList(aNumValues, ctypes.c_int32)
    cVals = _convertListToCtypeList(aValues, ctypes.c_double)
    cErrorFrame = ctypes.c_int32(0)
    error = _staticLib.LJM_eAddresses(handle, numFrames, ctypes.byref(cAddrs), ctypes.byref(cTypes), ctypes.byref(cWrites), ctypes.byref(cNumVals), ctypes.byref(cVals), ctypes.byref(cErrorFrame))
    if error != LJME_NOERROR:
        raise LJMError(error, cErrorFrame.value)
    return _convertCtypeListToList(cVals)
    
#LJM_ERROR_RETURN LJM_eNames(int Handle, int NumFrames, const char ** Names, int * aWrites, int * aNumValues, double * aValues, int * ErrorFrame);
def eNames(handle, numFrames, names, aWrites, aNumValues, aValues):
    cNames = _convertListToCtypeList(names, ctypes.c_char_p)
    cWrites = _convertListToCtypeList(aWrites, ctypes.c_int32)
    cNumVals = _convertListToCtypeList(aNumValues, ctypes.c_int32)
    cVals =  _convertListToCtypeList(aValues, ctypes.c_double)
    cErrorFrame = ctypes.c_int32(0)
    error = _staticLib.LJM_eNames(handle, numFrames, ctypes.byref(cNames), ctypes.byref(cWrites), ctypes.byref(cNumVals), ctypes.byref(cVals), ctypes.byref(cErrorFrame))
    if error != LJME_NOERROR:
        raise LJMError(error, cErrorFrame.value)
    return _convertCtypeListToList(cVals)
    
# Type conversion

#LJM_VOID_RETURN LJM_FLOAT32ToByteArray(const float * aFLOAT32, int RegisterOffset, int NumFLOAT32, unsigned char * aBytes);
def FLOAT32ToByteArray(aFLOAT32, registerOffset, numFLOAT32, aBytes):
    cFloats = _convertListToCtypeList(aFLOAT32, ctypes.c_float)
    cUbytes = _convertListToCtypeList(aBytes, ctypes.c_ubyte)
    _staticLib.LJM_FLOAT32ToByteArray(ctypes.byref(cFloats), registerOffset, numFLOAT32, ctypes.byref(cUbytes))
    return _convertCtypeListToList(cUbytes)
    
#LJM_VOID_RETURN LJM_ByteArrayToFLOAT32(const unsigned char * aBytes, int RegisterOffset, int NumFLOAT32, float * aFLOAT32);
def byteArrayToFLOAT32(aBytes, registerOffset, numFLOAT32, aFLOAT32):
    cUbytes = _convertListToCtypeList(aBytes, ctypes.c_ubyte)
    cFloats = _convertListToCtypeList(aFLOAT32, ctypes.c_float)
    _staticLib.LJM_ByteArrayToFLOAT32(ctypes.byref(cUbytes), registerOffset, numFLOAT32, ctypes.byref(cFloats))
    return _convertCtypeListToList(cFloats)
 
#LJM_VOID_RETURN LJM_UINT16ToByteArray(const unsigned short * aUINT16, int RegisterOffset, int NumUINT16, unsigned char * aBytes);
def UINT16ToByteArray(aUINT16, registerOffset, numUINT16, aBytes):
    cUint16 = _convertListToCtypeList(aUINT16, ctypes.c_uint16)
    cUbytes = _convertListToCtypeList(aBytes, ctypes.c_ubyte)
    _staticLib.LJM_UINT16ToByteArray(ctypes.byref(cUint16), registerOffset, numUINT16, ctypes.byref(cUbytes))
    return _convertCtypeListToList(cUbytes)
 
#LJM_VOID_RETURN LJM_ByteArrayToUINT16(const unsigned char * aBytes, int RegisterOffset, int NumUINT16, unsigned short * aUINT16);
def byteArrayToUINT16(aBytes, registerOffset, numUINT16, aUINT16):
    cUbytes = _convertListToCtypeList(aBytes, ctypes.c_ubyte)
    cUint16 = _convertListToCtypeList(aUINT16, ctypes.c_uint16)
    _staticLib.LJM_ByteArrayToUINT16(ctypes.byref(cUbytes), registerOffset, numUINT16, ctypes.byref(cUint16))
    return _convertCtypeListToList(cUint16)

#LJM_VOID_RETURN LJM_UINT32ToByteArray(const unsigned int * aUINT32, int RegisterOffset, int NumUINT32, unsigned char * aBytes);
def UINT32ToByteArray(aUINT32, registerOffset, numUINT32, aBytes):
    cUint32 = _convertListToCtypeList(aUINT32, ctypes.c_uint32)
    cUbytes = _convertListToCtypeList(aBytes, ctypes.c_ubyte)
    _staticLib.LJM_UINT32ToByteArray(ctypes.byref(cUint32), registerOffset, numUINT32, ctypes.byref(cUbytes))
    return _convertCtypeListToList(cUbytes)
    
#LJM_VOID_RETURN LJM_ByteArrayToUINT32(const unsigned char * aBytes, int RegisterOffset, int NumUINT32, unsigned int * aUINT32);
def byteArrayToUINT32(aBytes, registerOffset, numUINT32, aUINT32):
    cUbytes = _convertListToCtypeList(aBytes, ctypes.c_ubyte)
    cUint32 = _convertListToCtypeList(aUINT32, ctypes.c_uint32)
    _staticLib.LJM_ByteArrayToUINT32(ctypes.byref(cUbytes), registerOffset, numUINT32, ctypes.byref(cUint32))
    return _convertCtypeListToList(cUint32)

#LJM_VOID_RETURN LJM_INT32ToByteArray(const int * aINT32, int RegisterOffset, int NumINT32, unsigned char * aBytes);
def INT32ToByteArray(aINT32, registerOffset, numINT32, aBytes):
    cInt32 = _convertListToCtypeList(aINT32, ctypes.c_int32)
    cUbytes = _convertListToCtypeList(aBytes, ctypes.c_ubyte)
    _staticLib.LJM_INT32ToByteArray(ctypes.byref(cInt32), registerOffset, numINT32, ctypes.byref(cUbytes))
    return _convertCtypeListToList(cUbytes)

#LJM_VOID_RETURN LJM_ByteArrayToINT32(const unsigned char * aBytes, int RegisterOffset, int NumINT32, int * aINT32);
def byteArrayToINT32(aBytes, registerOffset, numINT32, aINT32):
    cUbytes = _convertListToCtypeList(aBytes, ctypes.c_ubyte)
    cInt32 = _convertListToCtypeList(aINT32, ctypes.c_int32)
    _staticLib.LJM_ByteArrayToINT32(ctypes.byref(cUbytes), registerOffset, numINT32, ctypes.byref(cInt32))
    return _convertCtypeListToList(cInt32)

## Functions end

## Constants

# Read/Write direction constants:
LJM_READ = 0
LJM_WRITE = 1

# Data types:
# Automatic endian conversion, if needed by the processor
LJM_UINT16 = 0
LJM_UINT32 = 1
LJM_INT32 = 2
LJM_FLOAT32 = 3

# Advanced users data type:
# Does not do any endianness conversion
LJM_BYTE = 99
LJM_STRING = 98
LJM_STRING_MAX_SIZE = 49

# namesToAddresses sets this when a register name is not found
LJM_INVALID_NAME_ADDRESS = -1
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
LJM_ctUSB = 1
LJM_ctTCP = 2

# TCP/Ethernet constants:
LJM_NO_IP_ADDRESS = 0
LJM_NO_PORT = 0
LJM_DEFAULT_PORT = 502
LJM_UNKNOWN_IP_ADDRESS = -1

# Identifier types:
LJM_DEMO_MODE = "-1"
LJM_idANY = 0

# addressesToMBFB Constants
LJM_DEFAULT_FEEDBACK_ALLOCATION_SIZE = 62
LJM_USE_DEFAULT_MAXBYTESPERMBFB = 0

# listAll Constants
LJM_LIST_ALL_SIZE = 128

LJM_MAX_USB_PACKET_NUM_BYTES = 64
LJM_MAX_TCP_PACKET_NUM_BYTES_T7 = 1400
LJM_MAX_TCP_PACKETS_NUM_BYTES_NON_T7 = 64

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
LJME_ATTRIBUTE_LOAD_FAILURE = 202

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
LJME_INTENT_NOT_READY = 1297

## Constants end

### Wrapper functions for LJM library end