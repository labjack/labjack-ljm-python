"""
Python wrapper for the LJM driver.

"""
import ctypes
import os
import struct

__version__ = "0.2.0"

## LJM Exception
class LJMError(Exception):
    """
    Custom Exception meant for dealing with LJM specific errors
    """
    def __init__(self, errorCode = None, errorFrame = None, errorString = ""):
        self._errorCode = errorCode
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

    def __str__(self):
        frameStr = ""
        errorCodeStr = ""
        #errorStr = ""
        if self._errorFrame is not None:
            frameStr = "Frame " + str(self._errorFrame) + ", "
        if self._errorCode is not None:
            errorCodeStr = "LJM library error code " + str(self._errorCode) + " "
        return frameStr + errorCodeStr + self._errorString
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
    def __init__(self, deviceType=0, connectionType=0, identifier="LJM_idANY", autoOpen=True):
        self._handle = None
        self.deviceType = None
        self.connectionType = None
        self.serialNumber = None
        self.ipAddress = None
        self.port = None
        self.maxBytesPerMB = None
        if autoOpen:
            if isinstance(deviceType, str) and str(connectionType) == "0":
                #Use string default value for connectionType
                connectionType = "LJM_ctANY"
            if isinstance(connectionType, str) and str(deviceType) == "0":
                #Use string default value for deviceType
                deviceType = "LJM_dtANY"

            try:
                self.open(deviceType, connectionType, identifier)
            except LJMError, le:
                if le.errorCode is not None:
                    raise le
                else:
                    try:
                        self.openS(deviceType, connectionType, identifier)
                    except LJMError, le:
                        if le.errorCode is not None:
                            raise le
                        else:
                            raise LJMError(errorString = "deviceType and connectionType both need to be integers or strings.")
            '''
            if isinstance(deviceType, str) and isinstance(connectionType, str):
                self.openS(deviceType, connectionType, str(identifier))
            elif str(deviceType).isdigit() and str(connectionType).isdigit():
                self.open(int(deviceType), int(connectionType), str(identifier))
            else:
                raise LJMError(errorString = "Device and connection types need to both be strings or integers.")
            '''
            self.getHandleInfo()

    def __del__(self):
        pass

    def openS(self, deviceType="LJM_dtANY", connectionType="LJM_ctANY", identifier="LJM_idANY"):
        if isinstance(deviceType, str) is False:
            raise LJMError(errorString = "deviceType needs to be a string.")
        if isinstance(connectionType, str) is False:
            raise LJMError(errorString = "connectionType needs to be a string.")
        identifier = str(identifier)
        cHandle = ctypes.c_int32(0)

        error = _staticLib.LJM_OpenS(deviceType, connectionType, identifier, ctypes.byref(cHandle))
        if error is not LJME_NOERROR:
           raise LJMError(error)

        self._handle = cHandle.value

    def open(self, deviceType=0, connectionType=0, identifier="LJM_idANY"):
        try:
            cDev = ctypes.c_int32(deviceType)
        except:
            raise LJMError(errorString = "deviceType needs to be an integer.")
        try:
            cConn = ctypes.c_int32(connectionType)
        except:
            raise LJMError(errorString = "connectionType needs to be an integer.")
        identifier = str(identifier)
        cHandle = ctypes.c_int32(0)
        
        error = _staticLib.LJM_Open(ctypes.byref(cDev), ctypes.byref(cConn), identifier, ctypes.byref(cHandle))
        if error is not LJME_NOERROR:
           raise LJMError(error)

        self._handle = cHandle.value
        self.deviceType = cDev.value
        self.connectionType = cConn.value

    def getHandleInfo(self):
        cDev = ctypes.c_int32(0)
        cConn = ctypes.c_int32(0)
        cSer = ctypes.c_int32(0)
        cIPAddr = ctypes.c_int32(0)
        cPort = ctypes.c_int32(0)
        cPktMax = ctypes.c_int32(0)
        
        error = _staticLib.LJM_GetHandleInfo(self._handle, ctypes.byref(cDev), ctypes.byref(cConn), ctypes.byref(cSer), ctypes.byref(cIPAddr), ctypes.byref(cPort), ctypes.byref(cPktMax))
        if error != LJME_NOERROR:
            raise LJMError(error)
        
        self.deviceType = cDev.value
        self.connectionType = cConn.value
        self.serialNumber = cSer.value
        self.ipAddress = cIPAddr.value
        self.port = cPort.value
        self.maxBytesPerMB = cPktMax.value
        
        return cDev.value, cConn.value, cSer.value, cIPAddr.value, cPort.value, cPktMax.value

    ##LJM_ResetConnection(int Handle);
    #resetConnection(self):

    def close(self):
        error = _staticLib.LJM_Close(self._handle)
        if error != LJME_NOERROR:
            raise LJMError(error)

    def MBFBComm(self, unitID, aMBFB):
        try:
            cUnitID = ctypes.c_ubyte(unitID)
        except:
            raise LJMError(errorString = "unitID needs to be an integer with a value between 0 to 255 (byte).")
        try:
            cMBFB = _convertListToCtypeList(aMBFB, ctypes.c_ubyte)
        except:
            raise LJMError(errorString = "aMBFB needs to be a list of integers with values between 0 to 255 (bytes).")
        cErrorFrame = ctypes.c_int32(0)
        
        error = _staticLib.LJM_MBFBComm(self._handle, unitID, ctypes.byref(cMBFB), ctypes.byref(cErrorFrame))
        if error != LJME_NOERROR:
            raise LJMError(error, cErrorFrame.value)
        
        return _convertCtypeListToList(cMBFB)

    def writeRaw(self, data):
        try:
            cData = _convertListToCtypeList(data, ctypes.c_ubyte)
        except:
            raise LJMError(errorString = "data needs to be a list of integers with values between 0 to 255 (bytes).")
        numBytes = len(cData)

        error = _staticLib.LJM_WriteRaw(self._handle, ctypes.byref(cData), numBytes)
        if error != LJME_NOERROR:
            raise LJMError(error)

    def readRaw(self, numBytes):
        try:
            cData = (ctypes.c_ubyte*numBytes)(0)
        except:
            raise LJMError(errorString = "numBytes needs to be an integer with a value greater than 0.")
        
        error = _staticLib.LJM_ReadRaw(self._handle, ctypes.byref(cData), numBytes)
        if error != LJME_NOERROR:
            raise LJMError(error)
        
        return _convertCtypeListToList(cData)

    def eWriteAddress(self, address, dataType, value):
        try:
            cAddr = ctypes.c_int32(address)
        except:
            raise LJMError(errorString = "address needs to be an integer.")
        try:
            cType = ctypes.c_int32(dataType)
        except:
            raise LJMError(errorString = "dataType needs to be an integer.")
        try:
            cVal = ctypes.c_double(value)
        except:
            raise LJMError(errorString = "value needs to be a float.")

        error = _staticLib.LJM_eWriteAddress(self._handle, cAddr, cType, cVal)
        if error != LJME_NOERROR:
            raise LJMError(error)
    
    def eReadAddress(self, address, dataType):
        try:
            cAddr = ctypes.c_int32(address)
        except:
            raise LJMError(errorString = "address needs to be an integer.")
        try:
            cType = ctypes.c_int32(dataType)
        except:
            raise LJMError(errorString = "dataType needs to be an integer.")
        cVal = ctypes.c_double(0)
        
        error = _staticLib.LJM_eReadAddress(self._handle, cAddr, cType, ctypes.byref(cVal))
        if error != LJME_NOERROR:
            raise LJMError(error)
        
        return cVal.value
    
    def eWriteName(self, name, value):
        if isinstance(name, str) is False:
            raise LJMError(errorString = "name needs to be a string.")
        try:
            cVal = ctypes.c_double(value)
        except:
            raise LJMError(errorString = "value needs to be a float.")
        
        error = _staticLib.LJM_eWriteName(self._handle, name, cVal)
        if error != LJME_NOERROR:
            raise LJMError(error)
    
    def eReadName(self, name):
        if isinstance(name, str) is False:
            raise LJMError(errorString = "name needs to be a string.")
        cVal = ctypes.c_double(0)
        
        error = _staticLib.LJM_eReadName(self._handle, name, ctypes.byref(cVal))
        if error != LJME_NOERROR:
            raise LJMError(error)
        
        return cVal.value
    
    def eReadAddresses(self, aAddresses, aDataTypes):
        try:
            cAddrs = _convertListToCtypeList(aAddresses, ctypes.c_int32)
        except:
            raise LJMError(errorString = "aAddresses needs to be a list of integers.")
        try:
            cTypes = _convertListToCtypeList(aDataTypes, ctypes.c_int32)
        except:
            raise LJMError(errorString = "aDataTypes needs to be a list of integers.")
        if len(cAddrs) != len(cTypes):
            raise LJMError(errorString = "aAddresses and aDataTypes lists need to be the same length.")
        numFrames = len(cAddrs)
        cVals = (ctypes.c_double*numFrames)(0)
        cErrorFrame = ctypes.c_int32(0)
        
        error = _staticLib.LJM_eReadAddresses(self._handle, numFrames, ctypes.byref(cAddrs), ctypes.byref(cTypes), ctypes.byref(cVals), ctypes.byref(cErrorFrame))
        if error != LJME_NOERROR:
            raise LJMError(error, cErrorFrame.value)
        
        return _convertCtypeListToList(cVals)
    
    def eWriteAddresses(self, aAddresses, aDataTypes, aValues):
        try:
            cAddrs = _convertListToCtypeList(aAddresses, ctypes.c_int32)
        except:
            raise LJMError(errorString = "aAddresses needs to be a list of integers.")
        try:
            cTypes = _convertListToCtypeList(aDataTypes, ctypes.c_int32)
        except:
            raise LJMError(errorString = "aDataTypes needs to be a list of integers.")
        try:
            cVals = _convertListToCtypeList(aValues, ctypes.c_double)
        except:
            raise LJMError(errorString = "aValues needs to be a list of floats.")
        if (len(cAddrs) == len(cTypes) and len(cTypes) == len(cVals)) is False:
            raise LJMError(errorString = "aAddresses, aDataTypes and aValues lists need to be the same length.")
        numFrames = len(cAddrs)
        cErrorFrame = ctypes.c_int32(0)
        
        error = _staticLib.LJM_eWriteAddresses(self._handle, numFrames, ctypes.byref(cAddrs), ctypes.byref(cTypes), ctypes.byref(cVals), ctypes.byref(cErrorFrame))
        if error != LJME_NOERROR:
            raise LJMError(error, cErrorFrame.value)
    
    def eReadNames(self, names):
        try:
            if all(isinstance(x, str) for x in names) is False:
                raise Exception()
            cNames = _convertListToCtypeList(names, ctypes.c_char_p)
        except:
            raise LJMError(errorString = "names needs to be a list of strings.")
        numFrames = len(cNames)
        cVals =  (ctypes.c_double*numFrames)(0)
        cErrorFrame = ctypes.c_int32(0)

        error = _staticLib.LJM_eReadNames(self._handle, numFrames, cNames, ctypes.byref(cVals), ctypes.byref(cErrorFrame))
        if error != LJME_NOERROR:
            raise LJMError(error, cErrorFrame.value)

        return _convertCtypeListToList(cVals)
    
    def eWriteNames(self, names, aValues):
        try:
            if all(isinstance(x, str) for x in names) is False:
                raise Exception()
            cNames = _convertListToCtypeList(names, ctypes.c_char_p)
        except:
            raise LJMError(errorString = "names needs to be a list of strings.")
        try:
            cVals = _convertListToCtypeList(aValues, ctypes.c_double)
        except:
            raise LJMError(errorString = "aValues needs to be a list of floats.")
        if len(cNames) != len(cVals):
            raise LJMError(errorString = "names and aValues lists need to be the same length.")
        numFrames = len(names)
        cErrorFrame = ctypes.c_int32(0)

        error = _staticLib.LJM_eWriteNames(self._handle, numFrames, ctypes.byref(cNames), ctypes.byref(cVals), ctypes.byref(cErrorFrame))
        if error != LJME_NOERROR:
            raise LJMError(error, cErrorFrame.value)
    
    def eAddresses(self, aAddresses, aDataTypes, aWrites, aNumValues, aValues=None):
        try:
            cAddrs = _convertListToCtypeList(aAddresses, ctypes.c_int32)
        except:
            raise LJMError(errorString = "aAddresses needs to be a list of integers.")
        try:
            cTypes = _convertListToCtypeList(aDataTypes, ctypes.c_int32)
        except:
            raise LJMError(errorString = "aDataTypes needs to be a list of integers.")
        try:
            cWrites = _convertListToCtypeList(aWrites, ctypes.c_int32)
        except:
            raise LJMError(errorString = "aWrites needs to be a list of integers.")
        try:
            cNumVals = _convertListToCtypeList(aNumValues, ctypes.c_int32)
        except:
            raise LJMError(errorString = "aNumValues needs to be a list of integers.")
        if (len(cAddrs) == len(cTypes) and len(cTypes) == len(cWrites) and len(cWrites) == len(cNumVals)) is False:
            raise LJMError(errorString = "aAddresses, aDataTypes, aWrites and aNumValues lists need to be the same length.")
        if all(x == LJM_READ for x in aWrites):
            #All reads
            cVals = (ctypes.c_double*(sum(aNumValues)))(0)
        else:
            #Not all reads.  User needs to pass aValues with the correct minimum length.
            try:
                cVals = _convertListToCtypeList(aValues, ctypes.c_double)
                if len(cVals) < sum(aNumValues):
                    raise Exception()
            except:
                raise LJMError(errorString = "aValues needs to be a list of floats with a length of at least " + str(sum(aNumValues)) + ".")        
        numFrames = len(cAddrs)
        cErrorFrame = ctypes.c_int32(0)

        error = _staticLib.LJM_eAddresses(self._handle, numFrames, ctypes.byref(cAddrs), ctypes.byref(cTypes), ctypes.byref(cWrites), ctypes.byref(cNumVals), ctypes.byref(cVals), ctypes.byref(cErrorFrame))
        if error != LJME_NOERROR:
            raise LJMError(error, cErrorFrame.value)

        return _convertCtypeListToList(cVals)
        
    def eNames(self, names, aWrites, aNumValues, aValues=None):
        try:
            if all(isinstance(x, str) for x in names) is False:
                raise Exception()
            cNames = _convertListToCtypeList(names, ctypes.c_char_p)
        except:
            raise LJMError(errorString = "names needs to be a list of strings.")
        try:
            cWrites = _convertListToCtypeList(aWrites, ctypes.c_int32)
        except:
            raise LJMError(errorString = "aWrites needs to be a list of integers.")
        try:
            cNumVals = _convertListToCtypeList(aNumValues, ctypes.c_int32)
        except:
            raise LJMError(errorString = "aNumValues needs to be a list of integers.")
        if (len(cNames) == len(cWrites) and len(cWrites) == len(cNumVals)) is False:
            raise LJMError(errorString = "names, aWrites and aNumValues lists need to be the same length.")
        if all(x == LJM_READ for x in aWrites):
            #All reads
            cVals = (ctypes.c_double*(sum(aNumValues)))(0)
        else:
            #Not all reads.  User needs to pass aValues with the correct minimum length.
            try:
                cVals = _convertListToCtypeList(aValues, ctypes.c_double)
                if len(cVals) < sum(aNumValues):
                    raise Exception()
            except:
                raise LJMError(errorString = "aValues needs to be a list of floats with a length of at least " + str(sum(aNumValues)) + ".")
        numFrames = len(cNames)
        cErrorFrame = ctypes.c_int32(0)

        error = _staticLib.LJM_eNames(self._handle, numFrames, ctypes.byref(cNames), ctypes.byref(cWrites), ctypes.byref(cNumVals), ctypes.byref(cVals), ctypes.byref(cErrorFrame))
        if error != LJME_NOERROR:
            raise LJMError(error, cErrorFrame.value)

        return _convertCtypeListToList(cVals)

## Device end

### Classes end

## Functions

#LJM_ERROR_RETURN LJM_AddressesToMBFB(int MaxBytesPerMBFB, int * aAddresses, int * aTypes, int * aWrites, int * aNumValues, double * aValues, int * NumFrames, unsigned char * aMBFBCommand);
def addressesToMBFB(maxBytesPerMBFB, aAddresses, aDataTypes, aWrites, aNumValues, aValues=None):
    try:
        cMaxBytes = ctypes.c_int32(maxBytesPerMBFB)
    except:
        raise LJMError(errorString = "maxBytesPerMBFB needs to be a integer.")
    try:
        cAddrs = _convertListToCtypeList(aAddresses, ctypes.c_int32)
    except:
        raise LJMError(errorString = "aAddresses needs to be a list of integers.")
    try:
        cTypes = _convertListToCtypeList(aDataTypes, ctypes.c_int32)
    except:
        raise LJMError(errorString = "aDataTypes needs to be a list of integers.")
    try:
        cWrites = _convertListToCtypeList(aWrites, ctypes.c_int32)
    except:
        raise LJMError(errorString = "aWrites needs to be a list of integers.")
    try:
        cNumVals = _convertListToCtypeList(aNumValues, ctypes.c_int32)
    except:
        raise LJMError(errorString = "aNumValues needs to be a list of integers.")
    if (len(cAddrs) == len(cTypes) and len(cTypes) == len(cWrites) and len(cWrites) == len(cNumVals)) is False:
        raise LJMError(errorString = "aAddresses, aDataTypes, aWrites and aValues lists need to be the same length.")
    if all(x == LJM_READ for x in aWrites):
        #All reads
        cVals = (ctypes.c_double*sum(aNumValues))(0)
    else:
        #Not all reads.  User needs to pass aValues with the correct minimum length.
        try:
            cVals = _convertListToCtypeList(aValues, ctypes.c_double)
            if len(cVals) < sum(aNumValues):
                raise Exception()
        except:
            raise LJMError(errorString = "aValues needs to be a list of floats with a length of at least " + str(sum(aNumValues)) + ".")
    numFrames = len(cAddrs)
    cNumFrames = ctypes.c_int32(numFrames)
    cComm = (ctypes.c_ubyte*maxBytesPerMBFB)(0)
    
    error = _staticLib.LJM_AddressesToMBFB(cMaxBytes, ctypes.byref(cAddrs), ctypes.byref(cTypes), ctypes.byref(cWrites), ctypes.byref(cNumVals), ctypes.byref(cVals), ctypes.byref(cNumFrames), ctypes.byref(cComm))
    if error != LJME_NOERROR:
        if _isWarningErrorCode(error):
            return cNumFrames.value, _convertCtypeListToList(cComm), error
        else:
            raise LJMError(error)
    
    return cNumFrames.value, _convertCtypeListToList(cComm)

#LJM_ERROR_RETURN LJM_UpdateValues(unsigned char * aMBFBResponse, int * aTypes, int * aWrites, int * aNumValues, int NumFrames, double * aValues);
def updateValues(aMBFBResponse, aDataTypes, aWrites, aNumValues):
    try:
        cMBFB = _convertListToCtypeList(aMBFBResponse, ctypes.c_ubyte)
    except:
        raise LJMError(errorString = "aMBFBResponse needs to be a list of integers with values between 0 to 255 (bytes).")
    try:
        cTypes = _convertListToCtypeList(aDataTypes, ctypes.c_int32)
    except:
        raise LJMError(errorString = "aDataTypes needs to be a list of integers.")
    try:
        cWrites = _convertListToCtypeList(aWrites, ctypes.c_int32)
    except:
        raise LJMError(errorString = "aWrites needs to be a list of integers.")
    try:
        cNumVals = _convertListToCtypeList(aNumValues, ctypes.c_int32)
    except:
        raise LJMError(errorString = "aNumValues needs to be a list of integers.")
    if (len(cTypes) == len(cWrites) and len(cWrites) == len(cNumVals)) is False:
        raise LJMError(errorString = "aDataTypes, aWrites and aValues lists need to be the same length.")
    numFrames = len(cTypes)
    cVals = (ctypes.c_double*(sum(aNumValues)))(0)
    
    error = _staticLib.LJM_UpdateValues(ctypes.byref(cMBFB), ctypes.byref(cTypes), ctypes.byref(cWrites), ctypes.byref(cNumVals), numFrames, ctypes.byref(cVals))
    if error != LJME_NOERROR:
        raise LJMError(error)

    return _convertCtypeListToList(cVals)

#LJM_ERROR_RETURN LJM_NamesToAddresses(int NumFrames, const char ** NamesIn, int * aAddressesOut, int * aTypesOut);
def namesToAddresses(namesIn):
    try:
        if all(isinstance(x, str) for x in namesIn) is False:
            raise Exception()
        cNames = _convertListToCtypeList(namesIn, ctypes.c_char_p)
    except:
        raise LJMError(errorString = "namesIn needs to be a list of strings.")
    numFrames = len(cNames)
    cAddrsOut = (ctypes.c_int32*numFrames)(0)
    cTypesOut = (ctypes.c_int32*numFrames)(0)
    
    error = _staticLib.LJM_NamesToAddresses(numFrames, ctypes.byref(cNames), ctypes.byref(cAddrsOut), ctypes.byref(cTypesOut))
    if error != LJME_NOERROR:
        raise LJMError(error)
    
    return _convertCtypeListToList(cAddrsOut), _convertCtypeListToList(cTypesOut)

#LJM_ERROR_RETURN LJM_NameToAddress(const char * NameIn, int * AddressOut, int * TypeOut);
def nameToAddress(nameIn):
    if isinstance(nameIn, str) is False:
        raise LJMError(errorString = "nameIn needs to be a string.")
    cAddrOut = ctypes.c_int32(0)
    cTypeOut = ctypes.c_int32(0)
    
    error = _staticLib.LJM_NameToAddress(nameIn, ctypes.byref(cAddrOut), ctypes.byref(cTypeOut))
    if error != LJME_NOERROR:
        raise LJMError(error)
    
    return cAddrOut.value, cTypeOut.value

#LJM_ERROR_RETURN LJM_ListAll(int DeviceType, int ConnectionType, int * NumFound, int * aSerialNumbers, int * aIPAddresses);
def listAll(deviceType, connectionType):
    try:
        cDev = ctypes.c_int32(deviceType)
    except:
        raise LJMError(errorString = "deviceType needs to be an integer.")
    try:
        cConn = ctypes.c_int32(connectionType)
    except:
        raise LJMError(errorString = "connectionType needs to be an integer.")
    
    cNumFound = ctypes.c_int32(0)
    cSerNums = (ctypes.c_int32*LJM_LIST_ALL_SIZE)(0)
    cIPAddrs = (ctypes.c_int32*LJM_LIST_ALL_SIZE)(0)
    
    error = _staticLib.LJM_ListAll(cDev, cConn, ctypes.byref(cNumFound), ctypes.byref(cSerNums), ctypes.byref(cIPAddrs))
    if error != LJME_NOERROR:
        if _isWarningErrorCode(error):
            return cNumFound.value, _convertCtypeListToList(cSerNums[0:cNumFound.value]), _convertCtypeListToList(cIPAddrs[0:cNumFound.value]), error
        else:
            raise LJMError(error)
    
    return cNumFound.value, _convertCtypeListToList(cSerNums[0:cNumFound.value]), _convertCtypeListToList(cIPAddrs[0:cNumFound.value])

#LJM_ERROR_RETURN LJM_ListAllS(const char * DeviceType, const char * ConnectionType, int * NumFound, int * aSerialNumbers, int * aIPAddresses);
def listAllS(deviceType, connectionType):
    if isinstance(deviceType, str) is False:
        raise LJMError(errorString = "deviceType needs to be a string.")
    if isinstance(connectionType, str) is False:
        raise LJMError(errorString = "connectionType needs to be a string.")
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

#LJM_VOID_RETURN LJM_ErrorToString(int ErrorCode, char * pString);
def errorToString(errorCode):
    try:
        cErr = ctypes.c_int32(errorCode)
    except:
        raise LJMError(errorString = "errorCode needs to be an integer.")
    errStr = " "*LJM_MAX_NAME_SIZE
    
    _staticLib.LJM_ErrorToString(cErr, errStr)
    
    return errStr.strip()

#LJM_VOID_RETURN LJM_LoadConstants();
def loadConstants():
    _staticLib.LJM_LoadConstants()

#LJM_ERROR_RETURN LJM_CloseAll();
def closeAll():
    error = _staticLib.LJM_CloseAll()
    if error != LJME_NOERROR:
        raise LJMError(error)

#LJM_ERROR_RETURN LJM_WriteLibraryConfigS(const char * Parameter, double Value);
def writeLibraryConfigS(parameter, value):
    if isinstance(parameter, str) is False:
        raise LJMError(errorString = "parameter needs to be a string.")
    try:
        cVal = ctypes.c_double(value)
    except:
        raise LJMError(errorString = "value needs to be a float.")
    
    error = _staticLib.LJM_WriteLibraryConfigS(parameter, cVal)
    if error != LJME_NOERROR:
        raise LJMError(error)
    
#LJM_ERROR_RETURN LJM_ReadLibraryConfigS(const char * Parameter, double * Value);
def readLibraryConfigS(parameter):
    if isinstance(parameter, str) is False:
        raise LJMError(errorString = "parameter needs to be a string.")
    cVal = ctypes.c_double(0)

    error = _staticLib.LJM_ReadLibraryConfigS(parameter, ctypes.byref(cVal))
    if error != LJME_NOERROR:
        raise LJMError(error)
    
    return cVal.value

#LJM_ERROR_RETURN LJM_NumberToIP(unsigned int Number, char * IPv4String);
def numberToIP(number):
    try:
        cNum = ctypes.c_uint32(number)
    except:
        raise LJMError(errorString = "number needs to be an integer.")
    IPv4String = " "*LJM_IPv4_STRING_SIZE

    error = _staticLib.LJM_NumberToIP(cNum, IPv4String)
    if error != LJME_NOERROR:
        raise LJMError(error)
    
    return IPv4String.strip()

#LJM_ERROR_RETURN LJM_IPToNumber(const char * IPv4String, unsigned int * Number);
def IPToNumber(IPv4String):
    if isinstance(IPv4String, str) is False:
        raise LJMError(errorString = "IPv4String needs to be a string.")
    #Make the sthe string is at least length LJM_IPv4_STRING_SIZE
    if len(IPv4String) < LJM_IPv4_STRING_SIZE:
        IPv4String += "\0"*(LJM_IPv4_STRING_SIZE-len(IPv4String))
    cNum = ctypes.c_uint32(0)
    
    error = _staticLib.LJM_IPToNumber(IPv4String, ctypes.byref(cNum));
    if error != LJME_NOERROR:
        raise LJMError(error)
    
    return cNum.value

#LJM_ERROR_RETURN LJM_NumberToMAC(unsigned long long Number, char * MACString);
def numberToMAC(number):
    try:
        cNum = ctypes.c_uint64(number)
    except:
        raise LJMError(errorString = "number needs to be long integer.")
    MACString = " "*LJM_MAC_STRING_SIZE

    error = _staticLib.LJM_NumberToMAC(number, MACString)
    if error != LJME_NOERROR:
        raise LJMError(error)
    
    return MACString.strip()

#LJM_ERROR_RETURN LJM_MACToNumber(const char * MACString, unsigned long long * Number);
def MACToNumber(MACString):
    if isinstance(MACString, str) is False:
        raise LJMError(errorString = "MACString needs to be a string.")
    #Make the sthe string is at least length LJM_MAC_STRING_SIZE
    if len(MACString) < LJM_MAC_STRING_SIZE:
        MACString += "\0"*(LJM_MAC_STRING_SIZE-len(MACString))
    cNum = ctypes.c_uint32(0)

    error = _staticLib.LJM_MACToNumber(MACString, ctypes.byref(cNum))
    if error != LJME_NOERROR:
        raise LJMError(error)
    
    return cNum.value

# Type conversion

#LJM_VOID_RETURN LJM_FLOAT32ToByteArray(const float * aFLOAT32, int RegisterOffset, int NumFLOAT32, unsigned char * aBytes);
def FLOAT32ToByteArray(aFLOAT32, registerOffset=0, numFLOAT32=None, aBytes=[]):
    try:
        cFloats = _convertListToCtypeList(aFLOAT32, ctypes.c_float)
    except:
        raise LJMError(errorString = "aFLOAT32 needs to be a list of floats.")
    try:
        cRegOffset = ctypes.c_int32(registerOffset)
        if registerOffset < 0:
            raise LJMError()
    except:
        raise LJMError(errorString = "registerOffset needs to be a non-negative integer.")
    if numFLOAT32 is None:
        numFLOAT32 = len(cFloats)
    try:
        cNumFloat = ctypes.c_int32(numFLOAT32)
        if numFLOAT32 < 1 or numFLOAT32 > len(cFloats):
            raise LJMError(numFLOAT32)
    except:
        raise LJMError(errorString = "numFLOAT32 needs to be a positive integer and cannot be larger than the length of the aFLOAT32 list.")
    numBytes = numFLOAT32*4 + registerOffset*2
    try:
        if len(aBytes) < numBytes:
            #Add the extra elements needed
            aBytes.extend([0]*(numBytes - len(aBytes)))
        cUbytes = _convertListToCtypeList(aBytes, ctypes.c_ubyte)
    except:
        raise LJMError(errorString = "aBytes needs to be a list of integers with values between 0 to 255 (bytes).")
        
    _staticLib.LJM_FLOAT32ToByteArray(ctypes.byref(cFloats), cRegOffset, cNumFloat, ctypes.byref(cUbytes))
    
    return _convertCtypeListToList(cUbytes)
    
#LJM_VOID_RETURN LJM_ByteArrayToFLOAT32(const unsigned char * aBytes, int RegisterOffset, int NumFLOAT32, float * aFLOAT32);
def byteArrayToFLOAT32(aBytes, registerOffset=0, numFLOAT32=None, aFLOAT32=[]):
    try:
        cUbytes = _convertListToCtypeList(aBytes, ctypes.c_ubyte)
    except:
        raise LJMError(errorString = "aBytes needs to be a list of integers with values between 0 to 255 (bytes).")
    try:
        cRegOffset = ctypes.c_int32(registerOffset)
        if registerOffset < 0:
            raise LJMError()
    except:
        raise LJMError(errorString = "registerOffset needs to be a non-negative integer.")
    if registerOffset > ((len(cUbytes)-4)/2):
        raise LJMError(errorString = "registerOffset value is too large for the aBytes list.")
    maxNum = int((len(cUbytes)-registerOffset*2)/4)
    if numFLOAT32 is None:
        numFLOAT32 = maxNum
    try:
        cNumFloat = ctypes.c_int32(numFLOAT32)
        if numFLOAT32 < 1:
            raise LJMError()
    except:
        raise LJMError(errorString = "numFLOAT32 needs to be a positive integer.")
    if numFLOAT32 > maxNum:
        raise LJMError(errorString = "numFLOAT32 value is too large for the aBytes list and the registerOffset value " + str(registerOffset) + ".")
    try:
        if len(aFLOAT32) < numFLOAT32:
            #Add the extra elements needed
            aFLOAT32.extend([0.0]*(numFLOAT32 - len(aFLOAT32)))
        cFloats = _convertListToCtypeList(aFLOAT32, ctypes.c_float)
    except:
        raise LJMError(errorString = "aFLOAT32 needs to be a list of floats.")

    _staticLib.LJM_ByteArrayToFLOAT32(ctypes.byref(cUbytes), cRegOffset, cNumFloat, ctypes.byref(cFloats))
    
    return _convertCtypeListToList(cFloats)
 
#LJM_VOID_RETURN LJM_UINT16ToByteArray(const unsigned short * aUINT16, int RegisterOffset, int NumUINT16, unsigned char * aBytes);
def UINT16ToByteArray(aUINT16, registerOffset=0, numUINT16=None, aBytes=[]):
    try:
        cUint16s = _convertListToCtypeList(aUINT16, ctypes.c_uint16)
    except:
        raise LJMError(errorString = "aUINT16 needs to be a list of integers with values between 0 to 65535 (unsigned 16-bit).")
    try:
        cRegOffset = ctypes.c_int32(registerOffset)
        if registerOffset < 0:
            raise LJMError()
    except:
        raise LJMError(errorString = "registerOffset needs to be a non-negative integer.")
    if numUINT16 is None:
        numUINT16 = len(cUint16s)
    try:
        cNumUint16 = ctypes.c_int32(numUINT16)
        if numUINT16 < 1 or numUINT16 > len(cUint16s):
            raise LJMError()
    except:
        raise LJMError(errorString = "numUINT16 needs to be a positive integer and cannot be larger than the length of the aUINT16 list.")
    numBytes = numUINT16*2 + registerOffset*2
    try:
        if len(aBytes) < numBytes:
            #Add the extra elements needed
            aBytes.extend([0]*(numBytes - len(aBytes)))
        cUbytes = _convertListToCtypeList(aBytes, ctypes.c_ubyte)
    except:
        raise LJMError(errorString = "aBytes needs to be a list of integers with values between 0 to 255 (bytes).")
    
    _staticLib.LJM_UINT16ToByteArray(ctypes.byref(cUint16s), cRegOffset, cNumUint16, ctypes.byref(cUbytes))
    
    return _convertCtypeListToList(cUbytes)
 
#LJM_VOID_RETURN LJM_ByteArrayToUINT16(const unsigned char * aBytes, int RegisterOffset, int NumUINT16, unsigned short * aUINT16);
def byteArrayToUINT16(aBytes, registerOffset=0, numUINT16=None, aUINT16=[]):
    try:
        cUbytes = _convertListToCtypeList(aBytes, ctypes.c_ubyte)
    except:
        raise LJMError(errorString = "aBytes needs to be a list of integers with values between 0 to 255 (bytes).")
    try:
        cRegOffset = ctypes.c_int32(registerOffset)
        if registerOffset < 0:
            raise LJMError()
    except:
        raise LJMError(errorString = "registerOffset needs to be a non-negative integer.")
    if registerOffset > ((len(cUbytes)-2)/2):
        raise LJMError(errorString = "registerOffset value is too large for the aBytes list.")
    maxNum = int((len(cUbytes)-registerOffset*2)/2)
    if numUINT16 is None:
        numUINT16 = maxNum
    try:
        cNumUint16 = ctypes.c_int32(numUINT16)
        if numUINT16 < 1:
            raise LJMError()
    except:
        raise LJMError(errorString = "numUINT16 needs to be a positive integer.")
    if numUINT16 > maxNum:
        raise LJMError(errorString = "numUINT16 value is too large for the aBytes list and the registerOffset value " + str(registerOffset) + ".")
    try:
        if len(aUINT16) < numUINT16:
            #Add the extra elements needed
            aUINT16.extend([0]*(numUINT16 - len(aUINT16)))
        cUint16s = _convertListToCtypeList(aUINT16, ctypes.c_uint16)
    except:
        raise LJMError(errorString = "aUINT16 needs to be a list of integers with values between 0 to 65535 (unsigned 16-bit).")
    
    _staticLib.LJM_ByteArrayToUINT16(ctypes.byref(cUbytes), cRegOffset, cNumUint16, ctypes.byref(cUint16s))
    
    return _convertCtypeListToList(cUint16s)

#LJM_VOID_RETURN LJM_UINT32ToByteArray(const unsigned int * aUINT32, int RegisterOffset, int NumUINT32, unsigned char * aBytes);
def UINT32ToByteArray(aUINT32, registerOffset=0, numUINT32=None, aBytes=[]):
    try:
        cUint32s = _convertListToCtypeList(aUINT32, ctypes.c_uint32)
    except:
        raise LJMError(errorString = "aUINT32 needs to be a list of integers (unsigned 32-bit).")
    try:
        cRegOffset = ctypes.c_int32(registerOffset)
        if registerOffset < 0:
            raise LJMError()
    except:
        raise LJMError(errorString = "registerOffset needs to be a non-negative integer.")
    if numUINT32 is None:
        numUINT32 = len(cUint32s)
    try:
        cNumUint32 = ctypes.c_int32(numUINT32)
        if numUINT32 < 1 or numUINT32 > len(cUint32s):
            raise LJMError()
    except:
        raise LJMError(errorString = "numUINT32 needs to be a positive integer and cannot be larger than the length of the aUINT32 list.")
    numBytes = numUINT32*4 + registerOffset*2
    try:
        if len(aBytes) < numBytes:
            #Add the extra elements needed
            aBytes.extend([0]*(numBytes - len(aBytes)))
        cUbytes = _convertListToCtypeList(aBytes, ctypes.c_ubyte)
    except:
        raise LJMError(errorString = "aBytes needs to be a list of integers with values between 0 to 255 (bytes).")
    
    _staticLib.LJM_UINT32ToByteArray(ctypes.byref(cUint32s), cRegOffset, cNumUint32, ctypes.byref(cUbytes))
    
    return _convertCtypeListToList(cUbytes)
    
#LJM_VOID_RETURN LJM_ByteArrayToUINT32(const unsigned char * aBytes, int RegisterOffset, int NumUINT32, unsigned int * aUINT32);
def byteArrayToUINT32(aBytes, registerOffset=0, numUINT32=None, aUINT32=[]):
    try:
        cUbytes = _convertListToCtypeList(aBytes, ctypes.c_ubyte)
    except:
        raise LJMError(errorString = "aBytes needs to be a list of integers with values between 0 to 255 (bytes).")
    try:
        cRegOffset = ctypes.c_int32(registerOffset)
        if registerOffset < 0:
            raise LJMError()
    except:
        raise LJMError(errorString = "registerOffset needs to be a non-negative integer.")
    if registerOffset > ((len(cUbytes)-4)/2):
        raise LJMError(errorString = "registerOffset value is too large for the aBytes list.")
    maxNum = int((len(cUbytes)-registerOffset*2)/4)
    if numUINT32 is None:
        numUINT32 = maxNum
    try:
        cNumUint32 = ctypes.c_int32(numUINT32)
        if numUINT32 < 1:
            raise LJMError()
    except:
        raise LJMError(errorString = "numUINT32 needs to be a positive integer.")
    if numUINT32 > maxNum:
        raise LJMError(errorString = "numUINT32 value is too large for the aBytes list and the registerOffset value " + str(registerOffset) + ".")
    try:
        if len(aUINT32) < numUINT32:
            #Add the extra elements needed
            aUINT32.extend([0]*(numUINT32 - len(aUINT32)))
        cUint32s = _convertListToCtypeList(aUINT32, ctypes.c_uint32)
    except:
        raise LJMError(errorString = "aUINT32 needs to be a list of integers (unsigned 32-bit).")

    _staticLib.LJM_ByteArrayToUINT32(ctypes.byref(cUbytes), cRegOffset, cNumUint32, ctypes.byref(cUint32s))
    
    return _convertCtypeListToList(cUint32s)

#LJM_VOID_RETURN LJM_INT32ToByteArray(const int * aINT32, int RegisterOffset, int NumINT32, unsigned char * aBytes);
def INT32ToByteArray(aINT32, registerOffset=0, numINT32=None, aBytes=[]):
    try:
        cInt32s = _convertListToCtypeList(aINT32, ctypes.c_int32)
    except:
        raise LJMError(errorString = "aINT32 needs to be a list of integers (signed 32-bit).")
    try:
        cRegOffset = ctypes.c_int32(registerOffset)
        if registerOffset < 0:
            raise LJMError()
    except:
        raise LJMError(errorString = "registerOffset needs to be a non-negative integer.")
    if numINT32 is None:
        numINT32 = len(cInt32s)
    try:
        cNumInt32 = ctypes.c_int32(numINT32)
        if numINT32 < 1 or numINT32 > len(cInt32s):
            raise LJMError()
    except:
        raise LJMError(errorString = "numINT32 needs to be a positive integer and cannot be larger than the length of the aINT32 list.")
    numBytes = numINT32*4 + registerOffset*2
    try:
        if len(aBytes) < numBytes:
            #Add the bytes needed
            aBytes.extend([0]*(numBytes - len(aBytes)))
        cUbytes = _convertListToCtypeList(aBytes, ctypes.c_ubyte)
    except:
        raise LJMError(errorString = "aBytes needs to be a list of integers with values between 0 to 255 (bytes).")
        
    _staticLib.LJM_INT32ToByteArray(ctypes.byref(cInt32s), cRegOffset, cNumInt32, ctypes.byref(cUbytes))
    
    return _convertCtypeListToList(cUbytes)

#LJM_VOID_RETURN LJM_ByteArrayToINT32(const unsigned char * aBytes, int RegisterOffset, int NumINT32, int * aINT32);
def byteArrayToINT32(aBytes, registerOffset=0, numINT32=None, aINT32=[]):
    try:
        cUbytes = _convertListToCtypeList(aBytes, ctypes.c_ubyte)
    except:
        raise LJMError(errorString = "aBytes needs to be a list of integers with values between 0 to 255 (bytes).")
    try:
        cRegOffset = ctypes.c_int32(registerOffset)
        if registerOffset < 0:
            raise LJMError()
    except:
        raise LJMError(errorString = "registerOffset needs to be a non-negative integer.")
    if registerOffset > ((len(cUbytes)-4)/2):
        raise LJMError(errorString = "registerOffset value is too large for the aBytes list.")
    maxNum = int((len(cUbytes)-registerOffset*2)/4)
    if numINT32 is None:
        numINT32 = maxNum
    try:
        cNumInt32 = ctypes.c_int32(numINT32)
        if numINT32 < 1:
            raise LJMError()
    except:
        raise LJMError(errorString = "numINT32 needs to be a positive integer.")
    if numINT32 > maxNum:
        raise LJMError(errorString = "numINT32 value is too large for the aBytes list and the registerOffset value " + str(registerOffset) + ".")
    try:
        if len(aINT32) < numINT32:
            #Add the extra elements needed
            aINT32.extend([0]*(numINT32 - len(aINT32)))
        cInt32s = _convertListToCtypeList(aINT32, ctypes.c_int32)
    except:
        raise LJMError(errorString = "aINT32 needs to be a list of integers (signed 32-bit).")
    
    _staticLib.LJM_ByteArrayToINT32(ctypes.byref(cUbytes), cRegOffset, cNumInt32, ctypes.byref(cInt32s))
    
    return _convertCtypeListToList(cInt32s)

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

## Functions end

## Constants from driver's header file

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

LJM_MAC_STRING_SIZE = 18
LJM_IPv4_STRING_SIZE = 16

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

# Config value names
LJM_SEND_RECEIVE_TIMEOUT_MS = "LJM_SEND_RECEIVE_TIMEOUT_MS"
LJM_OPEN_TCP_DEVICE_TIMEOUT_MS = "LJM_OPEN_TCP_DEVICE_TIMEOUT_MS"
LJM_LOG_MODE = "LJM_LOG_MODE"
LJM_LOG_LEVEL = "LJM_LOG_LEVEL"
LJM_VERSION = "LJM_VERSION"

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

# Library Errors:
LJME_LIBRARY_ERRORS_BEGIN = 1220
LJME_LIBRARY_ERRORS_END = 1399

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
LJME_ATTRIBUTE_LOAD_FAILURE = 1298
LJME_INVALID_CONFIG_NAME = 1299
## Constants end

### Wrapper functions for LJM library end