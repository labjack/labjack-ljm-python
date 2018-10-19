"""
Cross-platform wrapper for the LJM library.

"""
import ctypes
import sys

from labjack.ljm import constants
from labjack.ljm import errorcodes


STREAM_READ_CALLBACK = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int))

class CallbackData:
    def __init__(self, handle, callback):
        self.callbackUser = callback
        self.callbackWrapper = lambda arg: self.callbackUser(arg[0])
        self.callbackLjm = STREAM_READ_CALLBACK(self.callbackWrapper)
        self.argInner = ctypes.c_int(handle)
        self.argRef = ctypes.byref(self.argInner)
        # We need to keep references for the duration that stream is
        # running, otherwise the garbage collector will delete them
        # causing a segfault LJM tries to call our callback.

_g_callbackData = {}


class LJMError(Exception):
    """Custom exception class for LJM specific errors."""
    def __init__(self, errorCode=None, errorAddress=None, errorString=None):
        self._errorCode = errorCode
        self._errorAddress = errorAddress
        if errorString is None:
            self._errorString = ""
            try:
                if self._errorCode is not None:
                    self._errorString = errorToString(self._errorCode)
            except:
                pass
        else:
            self._errorString = str(errorString)

    @property
    def errorCode(self):
        return self._errorCode

    @property
    def errorAddress(self):
        return self._errorAddress

    @property
    def errorString(self):
        return self._errorString

    def __str__(self):
        addrStr = ""
        errorCodeStr = ""
        if self._errorAddress is not None:
            addrStr = "Address " + str(self._errorAddress) + ", "
        if self._errorCode is not None:
            errorCodeStr = "LJM library "
            if errorcodes.WARNINGS_BEGIN <= self._errorCode <= errorcodes.WARNINGS_END:
                errorCodeStr += "warning"
            else:
                errorCodeStr += "error"
            errorCodeStr += " code " + str(self._errorCode) + " "
        return addrStr + errorCodeStr + self._errorString


def _loadLibrary():
    """Returns a ctypes pointer to the LJM library."""
    try:
        libraryName = None
        try:
            if(sys.platform.startswith("win32") or sys.platform.startswith("cygwin")):
                # Windows
                libraryName = "LabJackM.dll"
            if(sys.platform.startswith("linux")):
                # Linux
                libraryName = "libLabJackM.so"
            if(sys.platform.startswith("darwin")):
                # Mac OS X
                libraryName = "libLabJackM.dylib"

            if libraryName is not None:
                if libraryName == "LabJackM.dll" and sys.platform.startswith("win32"):
                    return ctypes.WinDLL(libraryName)
                else:
                    return ctypes.CDLL(libraryName)
        except Exception:
            if(sys.platform.startswith("darwin")):
                # Mac OS X load failed. Try with absolute path.
                try:
                    libraryName = "/usr/local/lib/libLabJackM.dylib"
                    return ctypes.CDLL(libraryName)
                except Exception:
                    pass
            e = sys.exc_info()[1]
            raise LJMError(errorString="Cannot load the LJM library "+str(libraryName)+". "+str(e))

        # Unsupported operating system
        raise LJMError(errorString="Cannot load the LJM library. Unsupported platform "+sys.platform+".")
    except LJMError:
        ljme = sys.exc_info()[1]
        print(str(type(ljme)) + ": " + str(ljme))
        return None


_staticLib = _loadLibrary()


def listAll(deviceType, connectionType):
    """Scans for LabJack devices and returns lists describing the
    devices.

    Args:
        deviceType: An integer that filters which devices will be
            returned (labjack.ljm.constants.dtT7,
            labjack.ljm.constants.dtDIGIT, etc.).
            labjack.ljm.constants.dtANY is allowed.
        connectionType: An integer that filters by connection type
            (labjack.ljm.constants.ctUSB, labjack.ljm.constants.ctTCP,
            etc). labjack.ljm.constants.ctANY is allowed.

    Returns:
        A tuple containing:
        (numFound, aDeviceTypes, aConnectionTypes, aSerialNumbers,
         aIPAddresses)

        numFound: Number of devices found.
        aDeviceTypes: List of device types for each of the numFound
            devices.
        aConnectionTypes: List of connection types for each of the
            numFound devices.
        aSerialNumbers: List of serial numbers for each of the numFound
            devices.
        aIPAddresses: List of IP addresses for each of the numFound
            devices, but only if the connection type is TCP-based. For
            each corresponding device for which aIPAddresses[i] is not
            TCP-based, aIPAddresses[i] will be
            labjack.ljm.constants.NO_IP_ADDRESS.

    Raises:
        LJMError: An error was returned from the LJM library call.

    Note:
        This function only shows what devices can be opened. To
        actually open a device, use labjack.ljm.open/openS.

    """
    cDev = ctypes.c_int32(deviceType)
    cConn = ctypes.c_int32(connectionType)
    cNumFound = ctypes.c_int32(0)
    cDevTypes = (ctypes.c_int32*constants.LIST_ALL_SIZE)()
    cConnTypes = (ctypes.c_int32*constants.LIST_ALL_SIZE)()
    cSerNums = (ctypes.c_int32*constants.LIST_ALL_SIZE)()
    cIPAddrs = (ctypes.c_int32*constants.LIST_ALL_SIZE)()

    error = _staticLib.LJM_ListAll(cDev, cConn, ctypes.byref(cNumFound), ctypes.byref(cDevTypes), ctypes.byref(cConnTypes), ctypes.byref(cSerNums), ctypes.byref(cIPAddrs))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    numFound = cNumFound.value
    return numFound, _convertCtypeArrayToList(cDevTypes[0:numFound]), _convertCtypeArrayToList(cConnTypes[0:numFound]), _convertCtypeArrayToList(cSerNums[0:numFound]), _convertCtypeArrayToList(cIPAddrs[0:numFound])


def listAllS(deviceType, connectionType):
    """Scans for LabJack devices with string parameters and returns
    lists describing the devices.

    Args:
        deviceType: A string that filters which devices will be returned
            ("LJM_dtT7", etc.). "LJM_dtANY" is allowed.
        connectionType: A string that filters by connection type
            ("LJM_ctUSB", "LJM_ctTCP", etc).  "LJM_ctANY" is allowed.

    Returns:
        A tuple containing:
        (numFound, aDeviceTypes, aConnectionTypes, aSerialNumbers,
         aIPAddresses)

        numFound: Number of devices found.
        aDeviceTypes: List of device types for each of the numFound
            devices.
        aConnectionTypes: List of connection types for each of the
            numFound devices.
        aSerialNumbers: List of serial numbers for each of the numFound
            devices.
        aIPAddresses: List of IP addresses for each of the numFound
            devices, but only if the connection type is TCP-based. For
            each corresponding device for which aIPAddresses[i] is not
            TCP-based, aIPAddresses[i] will be
            labjack.ljm.constants.NO_IP_ADDRESS.

    Raises:
        TypeError: deviceType or connectionType are not strings.
        LJMError: An error was returned from the LJM library call.

    Note:
        This function only shows what devices can be opened. To
        actually open a device, use labjack.ljm.open/openS.

    """
    if not isinstance(deviceType, str):
        raise TypeError("Expected a string instead of " + str(type(deviceType)) + ".")
    if not isinstance(connectionType, str):
        raise TypeError("Expected a string instead of " + str(type(connectionType)) + ".")
    cNumFound = ctypes.c_int32(0)
    cDevTypes = (ctypes.c_int32*constants.LIST_ALL_SIZE)()
    cConnTypes = (ctypes.c_int32*constants.LIST_ALL_SIZE)()
    cSerNums = (ctypes.c_int32*constants.LIST_ALL_SIZE)()
    cIPAddrs = (ctypes.c_int32*constants.LIST_ALL_SIZE)()

    error = _staticLib.LJM_ListAllS(deviceType.encode("ascii"), connectionType.encode("ascii"), ctypes.byref(cNumFound), ctypes.byref(cDevTypes), ctypes.byref(cConnTypes), ctypes.byref(cSerNums), ctypes.byref(cIPAddrs))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    numFound = cNumFound.value
    return numFound, _convertCtypeArrayToList(cDevTypes[0:numFound]), _convertCtypeArrayToList(cConnTypes[0:numFound]), _convertCtypeArrayToList(cSerNums[0:numFound]), _convertCtypeArrayToList(cIPAddrs[0:numFound])


def listAllExtended(deviceType, connectionType, numAddresses, aAddresses, aNumRegs, maxNumFound):
    """Advanced version of listAll that performs an additional query of
    arbitrary registers on the device.

    Args:
        deviceType: An integer containing the type of the device to be
            connected (labjack.ljm.constants.dtT7,
            labjack.ljm.constants.dtDIGIT, etc.).
            labjack.ljm.constants.dtANY is allowed.
        connectionType: An integer that filters by connection type
            (labjack.ljm.constants.ctUSB,
            labjack.ljm.constants.ctTCP, etc.).
            labjack.ljm.constants.ctANY is allowed.
        numAddresses: The number of addresses to query. Also the size of
            aAddresses and aNumRegs.
        aAddresses: List of addresses to query for each device that is
            found.
        aNumRegs: List of the number of registers to query for each
            address. Each aNumRegs[i] corresponds to aAddresses[i].
        maxNumFound: The maximum number of devices to find.

    Returns:
        A tuple containing:
        (numFound, aDeviceTypes, aConnectionTypes, aSerialNumbers,
         aIPAddresses, aBytes)

        numFound: Number of devices found.
        aDeviceTypes: List of device types for each of the numFound
            devices.
        aConnectionTypes: List of connection types for each of the
            numFound devices.
        aSerialNumbers: List of serial numbers for each of the numFound
            devices.
        aIPAddresses: List of IP addresses for each of the numFound
            devices, but only if the connection type is TCP-based. For
            each corresponding device for which aIPAddresses[i] is not
            TCP-based, aIPAddresses[i] will be
            labjack.ljm.constants.NO_IP_ADDRESS.
        aBytes: List of the queried bytes sequentially. A device
            represented by index i will have an aBytes index of:
            (i * <the sum of aNumRegs> *
             labjack.ljm.constants.BYTES_PER_REGISTER).

    Raises:
        LJMError: An error was returned from the LJM library call.

    Note:
        This function only shows what devices can be opened. To
        actually open a device, use labjack.ljm.open/openS.

    """
    cDev = ctypes.c_int32(deviceType)
    cConn = ctypes.c_int32(connectionType)
    cNumAddrs = ctypes.c_int32(numAddresses)
    cAddrs = _convertListToCtypeArray(aAddresses, ctypes.c_int32)
    cNumRegs = _convertListToCtypeArray(aNumRegs, ctypes.c_int32)
    cMaxNumFound = ctypes.c_int32(maxNumFound)
    cNumFound = ctypes.c_int32(0)
    cDevTypes = (ctypes.c_int32*maxNumFound)()
    cConnTypes = (ctypes.c_int32*maxNumFound)()
    cSerNums = (ctypes.c_int32*maxNumFound)()
    cIPAddrs = (ctypes.c_int32*maxNumFound)()
    sumNumRegs = sum(aNumRegs[0:numAddresses])
    cBytes = (ctypes.c_ubyte*(maxNumFound*sumNumRegs*constants.BYTES_PER_REGISTER))()

    error = _staticLib.LJM_ListAllExtended(cDev, cConn, cNumAddrs, ctypes.byref(cAddrs), ctypes.byref(cNumRegs), cMaxNumFound, ctypes.byref(cNumFound), ctypes.byref(cDevTypes), ctypes.byref(cConnTypes), ctypes.byref(cSerNums), ctypes.byref(cIPAddrs), ctypes.byref(cBytes))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    numFound = cNumFound.value
    return numFound, _convertCtypeArrayToList(cDevTypes[0:numFound]), _convertCtypeArrayToList(cConnTypes[0:numFound]), _convertCtypeArrayToList(cSerNums[0:numFound]), _convertCtypeArrayToList(cIPAddrs[0:numFound]), _convertCtypeArrayToList(cBytes[0:(numFound*sumNumRegs*constants.BYTES_PER_REGISTER)])


def openS(deviceType="ANY", connectionType="ANY", identifier="ANY"):
    """Opens a LabJack device, and returns the device handle.

    Args:
        deviceType: A string containing the type of the device to be
            connected, optionally prepended by "LJM_dt". Possible values
            include "ANY", "T4", "T7", and "DIGIT".
        connectionType: A string containing the type of the connection
            desired, optionally prepended by "LJM_ct". Possible values
            include "ANY", "USB", "TCP", "ETHERNET", and "WIFI".
        identifier: A string identifying the device to be connected or
            "LJM_idANY"/"ANY". This can be a serial number, IP address,
            or device name. Device names may not contain periods.

    Returns:
        The new handle that represents a device connection upon success.

    Raises:
        TypeError: deviceType or connectionType are not strings.
        LJMError: An error was returned from the LJM library call.

    Note:
        Args are not case-sensitive, and empty strings indicate the
        same thing as "LJM_xxANY".

    """
    if not isinstance(deviceType, str):
        raise TypeError("Expected a string instead of " + str(type(deviceType)) + ".")
    if not isinstance(connectionType, str):
        raise TypeError("Expected a string instead of " + str(type(connectionType)) + ".")
    identifier = str(identifier)
    cHandle = ctypes.c_int32(0)

    error = _staticLib.LJM_OpenS(deviceType.encode("ascii"), connectionType.encode("ascii"), identifier.encode("ascii"), ctypes.byref(cHandle))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cHandle.value


def open(deviceType=constants.ctANY, connectionType=constants.ctANY, identifier="ANY"):
    """Opens a LabJack device, and returns the device handle.

    Args:
        deviceType: An integer containing the type of the device to be
            connected (labjack.ljm.constants.dtT4,
            labjack.ljm.constants.dtT7, labjack.ljm.constants.dtANY,
            etc.).
        connectionType: An integer containing the type of connection
            desired (labjack.ljm.constants.ctUSB,
            labjack.ljm.constants.ctTCP, labjack.ljm.constants.ctANY,
            etc.).
        identifier: A string identifying the device to be connected or
            "LJM_idANY"/"ANY". This can be a serial number, IP address,
            or device name. Device names may not contain periods.

    Returns:
        The new handle that represents a device connection upon success.

    Raises:
        TypeError: deviceType or connectionType are not integers.
        LJMError: An error was returned from the LJM library call.

    Notes:
        Args are not case-sensitive.
        Empty strings indicate the same thing as "LJM_xxANY".

    """
    cDev = ctypes.c_int32(deviceType)
    cConn = ctypes.c_int32(connectionType)
    identifier = str(identifier)
    cHandle = ctypes.c_int32(0)

    error = _staticLib.LJM_Open(cDev, cConn, identifier.encode("ascii"), ctypes.byref(cHandle))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cHandle.value


def getHandleInfo(handle):
    """Returns the device handle's details.

    Args:
        handle: A valid handle to an open device.

    Returns:
        A tuple containing:
        (deviceType, connectionType, serialNumber, ipAddress, port,
        maxBytesPerMB)

        deviceType: The device type corresponding to an integer
            constant such as labjack.ljm.constants.dtT7.
        connectionType: The output device type corresponding to an
            integer constant such as labjack.ljm.constants.ctUSB.
        serialNumber: The serial number of the device.
        ipAddress: The integer representation of the device's IP
            address when connectionType is TCP-based. If connectionType
            is not TCP-based, this will be
            labjack.ljm.constants.NO_IP_ADDRESS. The integer can be
            converted to a human-readable string with the
            labjack.ljm.numberToIP function.
        port: The port if the device connection is TCP-based, or the
            pipe if the device connection is USB based.
        maxBytesPerMB: The maximum packet size in number of bytes that
            can be sent or received from this device. This can change
            depending on connection and device type.

    Raises:
        LJMError: An error was returned from the LJM library call.

    Note:
        This function returns device information loaded during an open
        call and therefore does not initiate communications with the
        device. In other words, it is fast but will not represent
        changes to serial number or IP address since the device was
        opened.

    """
    cDev = ctypes.c_int32(0)
    cConn = ctypes.c_int32(0)
    cSer = ctypes.c_int32(0)
    cIPAddr = ctypes.c_int32(0)
    cPort = ctypes.c_int32(0)
    cPktMax = ctypes.c_int32(0)

    error = _staticLib.LJM_GetHandleInfo(handle, ctypes.byref(cDev), ctypes.byref(cConn), ctypes.byref(cSer), ctypes.byref(cIPAddr), ctypes.byref(cPort), ctypes.byref(cPktMax))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cDev.value, cConn.value, cSer.value, cIPAddr.value, cPort.value, cPktMax.value


def close(handle):
    """Closes the connection to the device.

    Args:
        handle: A valid handle to an open device.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    error = _staticLib.LJM_Close(handle)
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def closeAll():
    """Closes all connections to all devices.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    error = _staticLib.LJM_CloseAll()
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def cleanInfo(infoHandle):
    """Cleans/deallocates an infoHandle.

    Args:
        infoHandle: The info handle to clean/deallocate.

    Raises:
        LJMError: An error was returned from the LJM library call.

    Note:
        Calling cleanInfo on the same handle twice will cause error
        INVALID_INFO_HANDLE.

    """
    cInfo = ctypes.c_int32(infoHandle)
    error = _staticLib.LJM_CleanInfo(cInfo)
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def eWriteAddress(handle, address, dataType, value):
    """Performs Modbus operations that writes a value to a device.

    Args:
        handle: A valid handle to an open device.
        address: An address to write.
        dataTypes: The data type corresponding to the address
            (labjack.ljm.constants.FLOAT32, labjack.ljm.constants.INT32,
            etc.).
        value: The value to write.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    cAddr = ctypes.c_int32(address)
    cType = ctypes.c_int32(dataType)
    cVal = ctypes.c_double(value)

    error = _staticLib.LJM_eWriteAddress(handle, cAddr, cType, cVal)
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def eReadAddress(handle, address, dataType):
    """Performs Modbus operations that reads a value from a device.

    Args:
        handle: A valid handle to an open device.
        address: An address to read.
        dataTypes: The data type corresponding to the address
            (labjack.ljm.constants.FLOAT32, labjack.ljm.constants.INT32,
            etc.).

    Returns:
        The read value.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    cAddr = ctypes.c_int32(address)
    cType = ctypes.c_int32(dataType)
    cVal = ctypes.c_double(0)

    error = _staticLib.LJM_eReadAddress(handle, cAddr, cType, ctypes.byref(cVal))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cVal.value


def eWriteName(handle, name, value):
    """Performs Modbus operations that writes a value to a device.

    Args:
        handle: A valid handle to an open device.
        name: A name (string) to write.
        value: The value to write.

    Raises:
        TypeError: name is not a string.
        LJMError: An error was returned from the LJM library call.

    """
    if not isinstance(name, str):
        raise TypeError("Expected a string instead of " + str(type(name)) + ".")
    cVal = ctypes.c_double(value)

    error = _staticLib.LJM_eWriteName(handle, name.encode("ascii"), cVal)
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def eReadName(handle, name):
    """Performs Modbus operations that reads a value from a device.

    Args:
        handle: A valid handle to an open device.
        name: A name (string) to read.

    Returns:
        The read value.

    Raises:
        TypeError: name is not a string.
        LJMError: An error was returned from the LJM library call.

    """
    if not isinstance(name, str):
        raise TypeError("Expected a string instead of " + str(type(name)) + ".")
    cVal = ctypes.c_double(0)

    error = _staticLib.LJM_eReadName(handle, name.encode("ascii"), ctypes.byref(cVal))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cVal.value


def eReadAddresses(handle, numFrames, aAddresses, aDataTypes):
    """Performs Modbus operations that reads values from a device.

    Args:
        handle: A valid handle to an open device.
        numFrames: The total number of reads to perform.
        aAddresses: List of addresses to read. This list needs to be at
            least size numFrames.
        aDataTypes: List of data types corresponding to aAddresses
            (labjack.ljm.constants.FLOAT32, labjack.ljm.constants.INT32,
            etc.). This list needs to be at least size numFrames.

    Returns:
        A list of read values.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    cNumFrames = ctypes.c_int32(numFrames)
    cAddrs = _convertListToCtypeArray(aAddresses, ctypes.c_int32)
    cTypes = _convertListToCtypeArray(aDataTypes, ctypes.c_int32)
    cVals = (ctypes.c_double*numFrames)()
    cErrorAddr = ctypes.c_int32(-1)

    error = _staticLib.LJM_eReadAddresses(handle, cNumFrames, ctypes.byref(cAddrs), ctypes.byref(cTypes), ctypes.byref(cVals), ctypes.byref(cErrorAddr))
    if error != errorcodes.NOERROR:
        errAddr = cErrorAddr.value
        if errAddr == -1:
            errAddr = None
        raise LJMError(error, errAddr)

    return _convertCtypeArrayToList(cVals)


def eReadNames(handle, numFrames, aNames):
    """Performs Modbus operations that reads values from a device.

    Args:
        handle: A valid handle to an open device.
        numFrames: The total number of reads to perform.
        aNames: List of names (strings) to read. This list needs to be
            at least size numFrames.

    Returns:
        A list of read values.

    Raises:
        TypeError: aNames is not a list of strings.
        LJMError: An error was returned from the LJM library call.

    """
    cNumFrames = ctypes.c_int32(numFrames)
    asciiNames = []
    for x in aNames:
        if not isinstance(x, str):
            raise TypeError("Expected a string list but found an item " + str(type(x)) + ".")
        asciiNames.append(x.encode("ascii"))
    cNames = _convertListToCtypeArray(asciiNames, ctypes.c_char_p)
    cVals = (ctypes.c_double*numFrames)()
    cErrorAddr = ctypes.c_int32(-1)

    error = _staticLib.LJM_eReadNames(handle, cNumFrames, cNames, ctypes.byref(cVals), ctypes.byref(cErrorAddr))
    if error != errorcodes.NOERROR:
        errAddr = cErrorAddr.value
        if errAddr == -1:
            errAddr = None
        raise LJMError(error, errAddr)

    return _convertCtypeArrayToList(cVals)


def eWriteAddresses(handle, numFrames, aAddresses, aDataTypes, aValues):
    """Performs Modbus operations that writes values to a device.

    Args:
        handle: A valid handle to an open device.
        numFrames: The total number of writes to perform.
        aAddresses: List of addresses to write. This list needs to be at
            least size numFrames.
        aDataTypes: List of data types corresponding to aAddresses
            (labjack.ljm.constants.FLOAT32, labjack.ljm.constants.INT32,
            etc.). This list needs to be at least size numFrames.
        aValues: The list of values to write. This list needs to be at
            least size numFrames.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    cNumFrames = ctypes.c_int32(numFrames)
    cAddrs = _convertListToCtypeArray(aAddresses, ctypes.c_int32)
    cTypes = _convertListToCtypeArray(aDataTypes, ctypes.c_int32)
    cVals = _convertListToCtypeArray(aValues, ctypes.c_double)
    numFrames = len(cAddrs)
    cErrorAddr = ctypes.c_int32(-1)

    error = _staticLib.LJM_eWriteAddresses(handle, cNumFrames, ctypes.byref(cAddrs), ctypes.byref(cTypes), ctypes.byref(cVals), ctypes.byref(cErrorAddr))
    if error != errorcodes.NOERROR:
        errAddr = cErrorAddr.value
        if errAddr == -1:
            errAddr = None
        raise LJMError(error, errAddr)


def eWriteNames(handle, numFrames, aNames, aValues):
    """Performs Modbus operations that writes values to a device.

    Args:
        handle: A valid handle to an open device.
        numFrames: The total number of writes to perform.
        aNames: List of names (strings) to write. This list needs to be
            at least size numFrames.
        aValues: List of values to write. This list needs to be at least
            size numFrames.

    Raises:
        TypeError: aNames is not a list of strings.
        LJMError: An error was returned from the LJM library call.

    """
    cNumFrames = ctypes.c_int32(numFrames)
    asciiNames = []
    for x in aNames:
        if not isinstance(x, str):
            raise TypeError("Expected a string list but found an item " + str(type(x)) + ".")
        asciiNames.append(x.encode("ascii"))
    cNames = _convertListToCtypeArray(asciiNames, ctypes.c_char_p)
    cVals = _convertListToCtypeArray(aValues, ctypes.c_double)
    cErrorAddr = ctypes.c_int32(-1)

    error = _staticLib.LJM_eWriteNames(handle, cNumFrames, ctypes.byref(cNames), ctypes.byref(cVals), ctypes.byref(cErrorAddr))
    if error != errorcodes.NOERROR:
        errAddr = cErrorAddr.value
        if errAddr == -1:
            errAddr = None
        raise LJMError(error, errAddr)


def eReadAddressArray(handle, address, dataType, numValues):
    """Performs Modbus operations that reads values from a device.

    Args:
        handle: A valid handle to an open device.
        address: The address to read an array from.
        dataType: The data type of address.
        numValues: The size of the array to read.

    Returns:
        A list of size numValues with the read values.

    Raises:
        LJMError: An error was returned from the LJM library call.

    Note:
        If numValues is large enough, this functions will automatically
        split reads into multiple packets based on the current device's
        effective data packet size. Using both non-buffer and buffer
        registers in one function call is not supported.

    """
    cAddr = ctypes.c_int32(address)
    cType = ctypes.c_int32(dataType)
    cNumVals = ctypes.c_int32(numValues)
    cVals = (ctypes.c_double*numValues)()
    cErrorAddr = ctypes.c_int32(-1)

    error = _staticLib.LJM_eReadAddressArray(handle, cAddr, cType, cNumVals, ctypes.byref(cVals), ctypes.byref(cErrorAddr))
    if error != errorcodes.NOERROR:
        errAddr = cErrorAddr.value
        if errAddr == -1:
            errAddr = None
        raise LJMError(error, errAddr)

    return _convertCtypeArrayToList(cVals)


def eReadNameArray(handle, name, numValues):
    """Performs Modbus operations that reads values from a device.

    Args:
        handle: A valid handle to an open device.
        name: The register name to read an array from.
        numValues: The size of the array to read.

    Returns:
        A list of size numValues with the read values.

    Raises:
        TypeError: name is not a string.
        LJMError: An error was returned from the LJM library call.

    Note:
        If numValues is large enough, this functions will automatically
        split reads into multiple packets based on the current device's
        effective data packet size. Using both non-buffer and buffer
        registers in one function call is not supported.

    """
    if not isinstance(name, str):
        raise TypeError("Expected a string instead of " + str(type(name)) + ".")
    cNumVals = ctypes.c_int32(numValues)
    cVals = (ctypes.c_double*numValues)()
    cErrorAddr = ctypes.c_int32(-1)

    error = _staticLib.LJM_eReadNameArray(handle, name.encode("ascii"), cNumVals, ctypes.byref(cVals), ctypes.byref(cErrorAddr))
    if error != errorcodes.NOERROR:
        errAddr = cErrorAddr.value
        if errAddr == -1:
            errAddr = None
        raise LJMError(error, errAddr)

    return _convertCtypeArrayToList(cVals)


def eWriteAddressArray(handle, address, dataType, numValues, aValues):
    """Performs Modbus operations that writes values to a device.

    Args:
        handle: A valid handle to an open device.
        address: The address to write an array to.
        dataType: The data type of address.
        numValues: The size of the array to write.
        aValues: List of values to write. This list needs to be at least
            size numValues.

    Raises:
        LJMError: An error was returned from the LJM library call.

    Note:
        If numValues is large enough, this functions will automatically
        split writes into multiple packets based on the current
        device's effective data packet size. Using both non-buffer and
        buffer registers in one function call is not supported.

    """
    cAddr = ctypes.c_int32(address)
    cType = ctypes.c_int32(dataType)
    cNumVals = ctypes.c_int32(numValues)
    cVals = _convertListToCtypeArray(aValues, ctypes.c_double)
    cErrorAddr = ctypes.c_int32(-1)

    error = _staticLib.LJM_eWriteAddressArray(handle, cAddr, cType, cNumVals, ctypes.byref(cVals), ctypes.byref(cErrorAddr))
    if error != errorcodes.NOERROR:
        errAddr = cErrorAddr.value
        if errAddr == -1:
            errAddr = None
        raise LJMError(error, errAddr)


def eWriteNameArray(handle, name, numValues, aValues):
    """Performs Modbus operations that writes values to a device.

    Args:
        handle: A valid handle to an open device.
        name: The register name to write an array to.
        numValues: The size of the array to write.
        aValues: List of values to write. This list needs to be at least
            size numValues.

    Raises:
        TypeError: name is not a string.
        LJMError: An error was returned from the LJM library call.

    Note:
        If numValues is large enough, this functions will automatically
        split writes into multiple packets based on the current
        device's effective data packet size. Using both non-buffer and
        buffer registers in one function call is not supported.

    """
    if not isinstance(name, str):
        raise TypeError("Expected a string instead of " + str(type(name)) + ".")
    cNumVals = ctypes.c_int32(numValues)
    cVals = _convertListToCtypeArray(aValues, ctypes.c_double)
    cErrorAddr = ctypes.c_int32(-1)

    error = _staticLib.LJM_eWriteNameArray(handle, name.encode("ascii"), cNumVals, ctypes.byref(cVals), ctypes.byref(cErrorAddr))
    if error != errorcodes.NOERROR:
        errAddr = cErrorAddr.value
        if errAddr == -1:
            errAddr = None
        raise LJMError(error, errAddr)


def eReadAddressByteArray(handle, address, numBytes):
    """Performs a Modbus operation to read a byte array.

    Args:
        handle: A valid handle to an open device.
        address: The address to read an array from.
        numBytes: The size of the byte array to read.

    Returns:
        A list of size numBytes with the read byte values.

    Raises:
        LJMError: An error was returned from the LJM library call.

    Notes:
        This function will append a 0x00 byte to aBytes for
        odd-numbered numBytes.
        If numBytes is large enough, this functions will automatically
        split reads into multiple packets based on the current device's
        effective data packet size. Using both non-buffer and buffer
        registers in one function call is not supported.

    """
    cAddr = ctypes.c_int32(address)
    cNumBytes = ctypes.c_int32(numBytes)
    cBytes = (ctypes.c_ubyte*numBytes)()
    cErrorAddr = ctypes.c_int32(-1)

    error = _staticLib.LJM_eReadAddressByteArray(handle, cAddr, cNumBytes, ctypes.byref(cBytes), ctypes.byref(cErrorAddr))
    if error != errorcodes.NOERROR:
        errAddr = cErrorAddr.value
        if errAddr == -1:
            errAddr = None
        raise LJMError(error, errAddr)

    return _convertCtypeArrayToList(cBytes)


def eReadNameByteArray(handle, name, numBytes):
    """Performs a Modbus operation to read a byte array.

    Args:
        handle: A valid handle to an open device.
        name: The register name to read an array from.
        numBytes: The size of the byte array to read.

    Returns:
        A list of size numBytes with the read byte values.

    Raises:
        TypeError: name is not a string.
        LJMError: An error was returned from the LJM library call.

    Notes:
        This function will append a 0x00 byte to aBytes for
        odd-numbered numBytes.
        If numBytes is large enough, this functions will automatically
        split reads into multiple packets based on the current device's
        effective data packet size. Using both non-buffer and buffer
        registers in one function call is not supported.

    """
    if not isinstance(name, str):
        raise TypeError("Expected a string instead of " + str(type(name)) + ".")
    cNumBytes = ctypes.c_int32(numBytes)
    cBytes = (ctypes.c_ubyte*numBytes)()
    cErrorAddr = ctypes.c_int32(-1)

    error = _staticLib.LJM_eReadNameByteArray(handle, name.encode("ascii"), cNumBytes, ctypes.byref(cBytes), ctypes.byref(cErrorAddr))
    if error != errorcodes.NOERROR:
        errAddr = cErrorAddr.value
        if errAddr == -1:
            errAddr = None
        raise LJMError(error, errAddr)

    return _convertCtypeArrayToList(cBytes)


def eWriteAddressByteArray(handle, address, numBytes, aBytes):
    """Performs a Modbus operation to write a byte array.

    Args:
        handle: A valid handle to an open device.
        address: The register address to write a byte array to.
        numBytes: The size of the byte array to write.
        aBytes: List of byte values to write. This list needs to be at
            least size numBytes.

    Raises:
        LJMError: An error was returned from the LJM library call.

    Notes:
        This function will append a 0x00 byte to aBytes for
        odd-numbered numBytes.
        If numBytes is large enough, this functions will automatically
        split writes into multiple packets based on the current
        device's effective data packet size. Using both non-buffer and
        buffer registers in one function call is not supported.

    """
    cAddr = ctypes.c_int32(address)
    cNumBytes = ctypes.c_int32(numBytes)
    cBytes = _convertListToCtypeArray(aBytes, ctypes.c_ubyte)
    cErrorAddr = ctypes.c_int32(-1)

    error = _staticLib.LJM_eWriteAddressByteArray(handle, cAddr, cNumBytes, ctypes.byref(cBytes), ctypes.byref(cErrorAddr))
    if error != errorcodes.NOERROR:
        errAddr = cErrorAddr.value
        if errAddr == -1:
            errAddr = None
        raise LJMError(error, errAddr)


def eWriteNameByteArray(handle, name, numBytes, aBytes):
    """Performs a Modbus operation to write a byte array.

    Args:
        handle: A valid handle to an open device.
        name: The register name to write an array to.
        numBytes: The size of the byte array to write.
        aBytes: List of byte values to write. This list needs to be at
            least size numBytes.

    Raises:
        TypeError: name is not a string.
        LJMError: An error was returned from the LJM library call.

    Notes:
        This function will append a 0x00 byte to aBytes for
        odd-numbered numBytes.
        If numBytes is large enough, this functions will automatically
        split writes into multiple packets based on the current
        device's effective data packet size. Using both non-buffer and
        buffer registers in one function call is not supported.

    """
    if not isinstance(name, str):
        raise TypeError("Expected a string instead of " + str(type(name)) + ".")
    cNumBytes = ctypes.c_int32(numBytes)
    cBytes = _convertListToCtypeArray(aBytes, ctypes.c_ubyte)
    cErrorAddr = ctypes.c_int32(-1)

    error = _staticLib.LJM_eWriteNameByteArray(handle, name.encode("ascii"), cNumBytes, ctypes.byref(cBytes), ctypes.byref(cErrorAddr))
    if error != errorcodes.NOERROR:
        errAddr = cErrorAddr.value
        if errAddr == -1:
            errAddr = None
        raise LJMError(error, errAddr)


def eAddresses(handle, numFrames, aAddresses, aDataTypes, aWrites, aNumValues, aValues):
    """Performs Modbus operations that reads/writes values to a device.

    Args:
        handle: A valid handle to an open device.
        numFrames: The total number of reads/writes to perform.
        aAddresses: List of addresses to write. This list needs to be at
            least size numFrames.
        aDataTypes: List of data types corresponding to aAddresses
            (labjack.ljm.constants.FLOAT32, labjack.ljm.constants.INT32,
            etc.). This list needs to be at least size numFrames.
        aWrites: List of directions (labjack.ljm.constants.READ or
            labjack.ljm.constants.WRITE) corresponding to aAddresses.
            This list needs to be at least size numFrames.
        aNumValues: List of the number of values to read/write,
            corresponding to aWrites and aAddresses. This list needs to
            be at least size numFrames.
        aValues: List of values to write. This list needs to be the
            length of the sum of the aNumValues list's values. Values
            corresponding to writes are written.

    Returns:
        The list of aValues written/read.

    Raises:
        LJMError: An error was returned from the LJM library call.

    Notes:
        For every entry in aWrites[i] that is
        labjack.ljm.constants.WRITE, aValues contains aNumValues[i]
        values to write and for every entry in aWrites that is
        labjack.ljm.constants.READ, aValues contains aNumValues[i]
        values that will be updated in the returned list. aValues values
        must be in the same order as the rest of the lists. For example,
        if aWrite is:
            [labjack.ljm.constants.WRITE, labjack.ljm.constants.READ,
            labjack.ljm.constants.WRITE]
        and aNumValues is:
            [1, 4, 2]
        aValues would have one value to be written, then 4 blank/garbage
        values, and then 2 values to be written.

    """
    cNumFrames = ctypes.c_int32(numFrames)
    cAddrs = _convertListToCtypeArray(aAddresses, ctypes.c_int32)
    cTypes = _convertListToCtypeArray(aDataTypes, ctypes.c_int32)
    cWrites = _convertListToCtypeArray(aWrites, ctypes.c_int32)
    cNumVals = _convertListToCtypeArray(aNumValues, ctypes.c_int32)
    cVals = _convertListToCtypeArray(aValues, ctypes.c_double)
    cErrorAddr = ctypes.c_int32(-1)

    error = _staticLib.LJM_eAddresses(handle, cNumFrames, ctypes.byref(cAddrs), ctypes.byref(cTypes), ctypes.byref(cWrites), ctypes.byref(cNumVals), ctypes.byref(cVals), ctypes.byref(cErrorAddr))
    if error != errorcodes.NOERROR:
        errAddr = cErrorAddr.value
        if errAddr == -1:
            errAddr = None
        raise LJMError(error, errAddr)

    return _convertCtypeArrayToList(cVals)


def eNames(handle, numFrames, aNames, aWrites, aNumValues, aValues):
    """Performs Modbus operations that reads/writes values to a device.

    Args:
        handle: A valid handle to an open device.
        numFrames: The total number of reads/writes to perform.  This
            needs to be the length of aNames/aWrites/aNumValues or less.
        aNames: List of names (strings) to write/read. This list needs
            to be at least size numFrames.
        aWrites: List of directions (labjack.ljm.constants.READ or
            labjack.ljm.constants.WRITE) corresponding to aNames. This
            list needs to be at least size numFrames.
        aNumValues: List of the number of values to read/write,
            corresponding to aWrites and aNames. This list needs to be
            at least size numFrames.
        aValues: List of values to write.  This list needs to be the
            length of the sum of the aNumValues list's values.  Values
            corresponding to writes are written.

    Returns:
        The list of aValues written/read.

    Raises:
        TypeError: aNames is not a list of strings.
        LJMError: An error was returned from the LJM library call.

    Notes:
        For every entry in aWrites[i] that is
        labjack.ljm.constants.WRITE, aValues contains aNumValues[i]
        values to write and for every entry in aWrites that is
        labjack.ljm.constants.READ, aValues contains aNumValues[i]
        values that will be updated in the returned list. aValues values
        must be in the same order as the rest of the lists. For example,
        if aWrite is:
            [labjack.ljm.constants.WRITE, labjack.ljm.constants.READ,
            labjack.ljm.constants.WRITE]
        and aNumValues is:
            [1, 4, 2]
        aValues would have one value to be written, then 4 blank/garbage
        values, and then 2 values to be written.

    """
    cNumFrames = ctypes.c_int32(numFrames)
    asciiNames = []
    for x in aNames:
        if not isinstance(x, str):
            raise TypeError("Expected a string list but found an item " + str(type(x)) + ".")
        asciiNames.append(x.encode("ascii"))
    cNames = _convertListToCtypeArray(asciiNames, ctypes.c_char_p)
    cWrites = _convertListToCtypeArray(aWrites, ctypes.c_int32)
    cNumVals = _convertListToCtypeArray(aNumValues, ctypes.c_int32)
    cVals = _convertListToCtypeArray(aValues, ctypes.c_double)
    cErrorAddr = ctypes.c_int32(-1)

    error = _staticLib.LJM_eNames(handle, cNumFrames, ctypes.byref(cNames), ctypes.byref(cWrites), ctypes.byref(cNumVals), ctypes.byref(cVals), ctypes.byref(cErrorAddr))
    if error != errorcodes.NOERROR:
        raise LJMError(error, cErrorAddr.value)

    return _convertCtypeArrayToList(cVals)


def eReadNameString(handle, name):
    """Reads a string from a device.

    Args:
        handle: A valid handle to an open device.
        name: The string name of a register to read.

    Returns:
        The read string.

    Raises:
        TypeError: name is not a string.
        LJMError: An error was returned from the LJM library call.

    Note: This is a convenience function for eNames.

    """
    if not isinstance(name, str):
        raise TypeError("Expected a string instead of " + str(type(name)) + ".")
    outStr = ("\0"*constants.STRING_ALLOCATION_SIZE).encode("ascii")

    error = _staticLib.LJM_eReadNameString(handle, name.encode("ascii"), outStr)
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return _decodeASCII(outStr)


def eReadAddressString(handle, address):
    """Reads a string from a device.

    Args:
        handle: A valid handle to an open device.
        address: The integer address of a register to read.

    Returns:
        The read string.

    Raises:
        LJMError: An error was returned from the LJM library call.

    Note: This is a convenience function for eNames.

    """
    cAddr = ctypes.c_int32(address)
    outStr = ("\0"*constants.STRING_ALLOCATION_SIZE).encode("ascii")

    error = _staticLib.LJM_eReadAddressString(handle, cAddr, outStr)
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return _decodeASCII(outStr)


def eWriteNameString(handle, name, string):
    """Writes a string to a device.

    Args:
        handle: A valid handle to an open device.
        name: The string name of a register to write.
        string: The string to write.

    Raises:
        TypeError: name is not a string.
        LJMError: An error was returned from the LJM library call.

    Note: This is a convenience function for eNames.

    """
    if not isinstance(name, str):
        raise TypeError("Expected a string instead of " + str(type(name)) + ".")
    if not isinstance(string, str):
        raise TypeError("Expected a string instead of " + str(type(string)) + ".")

    error = _staticLib.LJM_eWriteNameString(handle, name.encode("ascii"), string.encode("ascii"))
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def eWriteAddressString(handle, address, string):
    """Writes a string to a device.

    Args:
        handle: A valid handle to an open device.
        address: The integer address of a register to write.
        string: The string to write.

    Raises:
        TypeError: string parameter is not a string.
        LJMError: An error was returned from the LJM library call.

    Note: This is a convenience function for eNames.

    """
    cAddr = ctypes.c_int32(address)
    if not isinstance(string, str):
        raise TypeError("Expected a string instead of " + str(type(string)) + ".")

    error = _staticLib.LJM_eWriteAddressString(handle, cAddr, string.encode("ascii"))
    if error != errorcodes.NOERROR:
        raise LJMError(error)


_g_eStreamDataSize = {}


def eStreamStart(handle, scansPerRead, numAddresses, aScanList, scanRate):
    """Initializes a stream object and begins streaming. This includes
       creating a buffer in LJM that collects data from the device.

    Args:
        handle: A valid handle to an open device.
        scansPerRead: Number of scans returned by each call to the
            eStreamRead function. This is not tied to the maximum
            packet size for the device.
        numAddresses: The size of aScanList. The number of addresses to
            scan.
        aScanList: List of Modbus addresses to collect samples from,
            per scan.
        scanRate: Sets the desired number of scans per second.

    Returns:
        The actual scan rate the device will scan at.

    Raises:
        LJMError: An error was returned from the LJM library call.

    Notes:
        Address configuration such as range, resolution, and
        differential voltages must be handled elsewhere.
        Check your device's documentation for valid aScanList channels.

    """
    cSPR = ctypes.c_int32(scansPerRead)
    cNumAddrs = ctypes.c_int32(numAddresses)
    cSL_p = _convertListToCtypeArray(aScanList, ctypes.c_int32)
    cScanRate = ctypes.c_double(scanRate)
    _g_eStreamDataSize[handle] = scansPerRead*numAddresses

    error = _staticLib.LJM_eStreamStart(handle, cSPR, cNumAddrs, ctypes.byref(cSL_p), ctypes.byref(cScanRate))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cScanRate.value


def eStreamRead(handle):
    """Returns data from an initialized and running LJM stream buffer.
    Waits for data to become available, if necessary.

    Args:
        handle: A valid handle to an open device.

    Returns:
        A tuple containing:
        (aData, deviceScanBacklog, ljmScanBackLog)

        aData: Stream data list with all channels interleaved. It will
            contain scansPerRead*numAddresses values configured from
            eStreamStart. The data returned is removed from the LJM
            stream buffer.
        deviceScanBacklog: The number of scans left in the device
            buffer, as measured from when data was last collected from
            the device. This should usually be near zero and not
            growing.
        ljmScanBacklog: The number of scans left in the LJM buffer, as
            measured from after the data returned from this function is
            removed from the LJM buffer. This should usually be near
            zero and not growing.

    Raises:
        LJMError: An error was returned from the LJM library call or
            eStreamStart was not called first on the handle and
            the aData size cannot be determined.

    """
    # May need to change to optimize
    if handle not in _g_eStreamDataSize:
        raise LJMError(errorString="Streaming has not been started for the given handle. Please call eStreamStart first.")
    cData = (ctypes.c_double*_g_eStreamDataSize[handle])()
    cD_SBL = ctypes.c_int32(0)
    cLJM_SBL = ctypes.c_int32(0)

    error = _staticLib.LJM_eStreamRead(handle, ctypes.byref(cData), ctypes.byref(cD_SBL), ctypes.byref(cLJM_SBL))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return _convertCtypeArrayToList(cData), cD_SBL.value, cLJM_SBL.value


def setStreamCallback(handle, callback):
    """Sets a callback that is called by LJM when the stream has
    collected scansPerRead scans (see eStreamStart) or if an error has
    occurred.

    Args:
        handle: A valid handle to an open device.
        callback: The callback function for LJM's stream thread to call
            when stream data is ready, which should call
            LJM_eStreamRead to acquire data. The handle will be the
            single argument of the callback.

    Raises:
        LJMError: An error was returned from the LJM library call.

    Notes:
        setStreamCallback should be called after eStreamStart.
        To disable the previous callback for stream reading, pass None
        as callback.
        setStreamCallback may not be called from within a callback.
        callback may not use data stored in `threading.local`.
        The handle is passed as the argument to callback because if you
        have multiple devices running with setStreamCallback, you might
        want to check which handle had stream data ready.

    """
    cbData = CallbackData(handle, callback)
    _g_callbackData[handle] = cbData
    cbLjm = cbData.callbackLjm
    cbArg = cbData.argRef

    error = _staticLib.LJM_SetStreamCallback(handle, cbLjm, cbArg)
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def eStreamStop(handle):
    """Stops the LJM library from streaming any more data from the
    device, while leaving any collected data in the LJM library's
    buffer to be read. Stops the device from streaming.

    Args:
        handle: A valid handle to an open device.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    if handle in _g_eStreamDataSize:
        del _g_eStreamDataSize[handle]
    if handle in _g_callbackData:
        del _g_callbackData[handle]

    error = _staticLib.LJM_eStreamStop(handle)
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def streamBurst(handle, numAddresses, aScanList, scanRate, numScans):
    """Initializes a stream burst and collects data. This function
    combines eStreamStart, eStreamRead, and eStreamStop, as well as some
    other device initialization.

    Args:
        handle: A valid handle to an open device.
        numAddresses: The size of aScanList. The number of addresses to
            scan.
        aScanList: A list of Modbus addresses to collect samples from,
            per scan.
        scanRate: Sets the desired number of scans per second.
            Upon successful return of this function, gets updated to
            the actual scan rate that the device scanned at.
        numScans: The number of scans to collect. This is how many burst
            scans are collected and may not be zero.

    Returns:
        A tuple containing:
        (scanRate, aData)

        scanRate: The actual scan rate that the device scanned at.
        aData: List of streamed data. Returns all addresses
            interleaved. This will hold (numScans * numAddresses)
            values.

    Raises:
        LJMError: An error was returned from the LJM library call.

    Notes:
        Address configuration such as range, resolution, and
        differential voltages are handled by writing to the device.
        Check your device's documentation for which addresses are valid
        for aScanList and how many burst scans may be collected.
        This function will block for (numScans / scanRate) seconds or
        longer.

    """
    cNumAddresses = ctypes.c_int32(numAddresses)
    cScanList_p = _convertListToCtypeArray(aScanList, ctypes.c_int32)
    cScanRate = ctypes.c_double(scanRate)
    cNumScans = ctypes.c_uint32(numScans)
    cData = (ctypes.c_double*(numScans*numAddresses))()

    error = _staticLib.LJM_StreamBurst(handle, cNumAddresses, ctypes.byref(cScanList_p), ctypes.byref(cScanRate), cNumScans, ctypes.byref(cData))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cScanRate.value, _convertCtypeArrayToList(cData)


def writeRaw(handle, data, numBytes=None):
    """Sends an unaltered data packet to a device.

    Args:
        handle: A valid handle to an open device.
        data: The byte list/packet to send.
        numBytes: The number of bytes to send.  Default is None and will
            automaticcally send all the bytes in the data list.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    cData = _convertListToCtypeArray(data, ctypes.c_ubyte)
    if numBytes is None:
        numBytes = len(cData)
    cNumBytes = ctypes.c_int32(numBytes)

    error = _staticLib.LJM_WriteRaw(handle, ctypes.byref(cData), cNumBytes)
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def readRaw(handle, numBytes):
    """Reads an unaltered data packet from a device.

    Args:
        handle: A valid handle to an open device.
        numBytes: The number of bytes to receive.

    Returns:
        A list that is the read byte packet. It is length numBytes.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    cNumBytes = ctypes.c_int32(numBytes)
    cData = (ctypes.c_ubyte*numBytes)()

    error = _staticLib.LJM_ReadRaw(handle, ctypes.byref(cData), cNumBytes)
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return _convertCtypeArrayToList(cData)


def addressesToMBFB(maxBytesPerMBFB, aAddresses, aDataTypes, aWrites, aNumValues, aValues, numFrames, aMBFBCommand=None):
    """Takes in lists that together represent operations to be performed
    on a device and returns the numbers of frames created and a byte
    list representing a valid Modbus Feedback command.

    Args:
        maxBytesPerMBFB: The maximum number of bytes that the Feedback
            command is allowed to consist of. It is highly recommended
            to pass the size of MaxBytesPerMBFB to prevent buffer
            overflow.
        aAddresses: A list of size numFrames representing the register
            addresses to read from or write to for each frame.
        aDataTypes: A list of size numFrames representing the data types
            to read or write. See the Data Type constants in the
            labjack.ljm.constants module.
        aWrites: A list of size numFrames of the direction/access
            direction/access type (labjack.ljm.constants.READ or
            labjack.ljm.constants.WRITE) for each frame.
        aNumValues: A list of size numFrames giving the number of values
            to read/write for each frame.
        aValues: A list of values to write. Needs to be the length of
            the sum of the aNumValues list's values. Values
            corresponding to writes are written.
        numFrames: The number of frames to be created, which should be
            the length of aAddresses/aTypes/aWrites/aNumValues or less.
        aMBFBCommand: The Feedback command to be passed.  This should be
            at least the size maxBytesPerMBFB. Default is None, which
            creates this list with size maxBytesPerMBFB. Transaction ID
            and Unit ID will be blanks that mbfbComm will fill in.

    Returns:
        A tuple containing:
        (numFrames, aMBFBCommand)

        numFrames: The number of frames created.
        aMBFBCommand: A list representing the Modbus Feedback command.

    Raises:
        LJMError: An error was returned from the LJM library call.

    Notes:
        For every entry in aWrites[i] that is
        labjack.ljm.constants.WRITE, aValues contains aNumValues[i]
        values to write and for every entry in aWrites that is
        labjack.ljm.constants.READ, aValues contains aNumValues[i]
        values that will later be updated in the updateValues function.
        aValues values must be in the same order as the rest of the
        lists. For example, if aWrite is:
            [labjack.ljm.constants.WRITE, labjack.ljm.constants.READ,
            labjack.ljm.constants.WRITE]
        and aNumValues is:
            [1, 4, 2]
        aValues would have one value to be written, then 4 blank/garbage
        values, and then 2 values to be written.

    """
    cMaxBytes = ctypes.c_int32(maxBytesPerMBFB)
    cAddrs = _convertListToCtypeArray(aAddresses, ctypes.c_int32)
    cTypes = _convertListToCtypeArray(aDataTypes, ctypes.c_int32)
    cWrites = _convertListToCtypeArray(aWrites, ctypes.c_int32)
    cNumVals = _convertListToCtypeArray(aNumValues, ctypes.c_int32)
    cVals = _convertListToCtypeArray(aValues, ctypes.c_double)
    cNumFrames = ctypes.c_int32(numFrames)
    if aMBFBCommand is None:
        cComm = (ctypes.c_ubyte*maxBytesPerMBFB)()
    else:
        cComm = _convertListToCtypeArray(aMBFBCommand, ctypes.c_ubyte)

    error = _staticLib.LJM_AddressesToMBFB(cMaxBytes, ctypes.byref(cAddrs), ctypes.byref(cTypes), ctypes.byref(cWrites), ctypes.byref(cNumVals), ctypes.byref(cVals), ctypes.byref(cNumFrames), ctypes.byref(cComm))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cNumFrames.value, _convertCtypeArrayToList(cComm)


def mbfbComm(handle, unitID, aMBFB):
    """Sends a Modbus Feedback command and receives a Feedback response,
    and parses the response for obvious errors. This function adds its
    own Transaction ID to the command.

    Args:
        handle: A valid handle to an open device.
        unitID: The ID of the specific unit that the Modbus Feedback
            command should be sent to. Primarily used for LabJack Mote
            communication.
        aMBFB: A list that is the Modbus Feedback command to send. This
            must also be a size large enough for the Feedback response.

    Return:
        A list that is the Modbus Feedback reponse.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    cUnitID = ctypes.c_ubyte(unitID)
    cMBFB = _convertListToCtypeArray(aMBFB, ctypes.c_ubyte)
    cErrorAddr = ctypes.c_int32(-1)

    error = _staticLib.LJM_MBFBComm(handle, unitID, ctypes.byref(cMBFB), ctypes.byref(cErrorAddr))
    if error != errorcodes.NOERROR:
        errAddr = cErrorAddr.value
        if errAddr == -1:
            errAddr = None
        raise LJMError(error, errAddr)

    return _convertCtypeArrayToList(cMBFB)


def updateValues(aMBFBResponse, aDataTypes, aWrites, aNumValues, numFrames, aValues=None):
    """Takes a Modbus Feedback response from a device and the lists
    corresponding the Feedback command, and returns the converted
    response values.

    Args:
        aDataTypes: The list of data types read/written.
        aWrites: The list of read/write directions.
        aNumValues: The list of how many values were read/written.
        numFrames: The number of frames read/written.
        aValues: A list of values to pass.  This should be at least the
            sum of the values in the aNumValues list. Default is None,
            which creates this list with a size of the sum of the values
            in the aNumValues list.

    Returns:
        A list of converted float values from the Modbus Feedback
        response.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    cMBFB = _convertListToCtypeArray(aMBFBResponse, ctypes.c_ubyte)
    cTypes = _convertListToCtypeArray(aDataTypes, ctypes.c_int32)
    cWrites = _convertListToCtypeArray(aWrites, ctypes.c_int32)
    cNumVals = _convertListToCtypeArray(aNumValues, ctypes.c_int32)
    cNumFrames = ctypes.c_int32(numFrames)
    if aValues is None:
        cVals = (ctypes.c_double*(sum(aNumValues)))()
    else:
        cVals = _convertListToCtypeArray(aValues, ctypes.c_double)

    error = _staticLib.LJM_UpdateValues(ctypes.byref(cMBFB), ctypes.byref(cTypes), ctypes.byref(cWrites), ctypes.byref(cNumVals), cNumFrames, ctypes.byref(cVals))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return _convertCtypeArrayToList(cVals)


def namesToAddresses(numFrames, aNames, aAddresses=None, aDataTypes=None):
    """Takes a list of Modbus register names and returns two lists
    containing the corresponding addresses and data types.

    Args:
        numFrames: The number of names in aNames, and minimum size of
            aAddresses and aDataTypes if not set to None.
        aNames: List of strings containing the register name or register
            alternate name.
        aAddresses: List of addresses to pass. This should be at least
            the size numFrames. Default is None, which creates this list
            with size of numFrames and filled with zeros.
        aDataTypes: List of data types to pass. This should be at least
            the size numFrames. Default is None, which creates this list
            with size of numFrames and filled with zeros.

    Returns:
        A tuple containing:
        (aAddresses, aDataTypes)

        aAddresses: A list of addresses corresponding to the register
            names list.
        aDataTypes: A list of data types corresponding to the register
            names list.

    Raises:
        TypeError: names is not a list of strings.
        LJMError: An error was returned from the LJM library call.

    Note: For each register identifier in aNames that is invalid, the
        corresponding aAddresses value will be set to
        labjack.ljm.constants.INVALID_NAME_ADDRESS.

    """
    cNumFrames = ctypes.c_int32(numFrames)
    asciiNames = []
    for x in aNames:
        if not isinstance(x, str):
            raise TypeError("Expected a string list but found an item " + str(type(x)) + ".")
        asciiNames.append(x.encode("ascii"))
    cNames = _convertListToCtypeArray(asciiNames, ctypes.c_char_p)
    if aAddresses is None:
        cAddrs = (ctypes.c_int32*numFrames)()
    else:
        cAddrs = _convertListToCtypeArray(aAddresses, ctypes.c_int32)
    if aDataTypes is None:
        cTypes = (ctypes.c_int32*numFrames)()
    else:
        cTypes = _convertListToCtypeArray(aDataTypes, ctypes.c_int32)

    error = _staticLib.LJM_NamesToAddresses(cNumFrames, ctypes.byref(cNames), ctypes.byref(cAddrs), ctypes.byref(cTypes))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return _convertCtypeArrayToList(cAddrs), _convertCtypeArrayToList(cTypes)


def nameToAddress(name):
    """Takes a Modbus register name and returns the corresponding
    address and data type values.

    Args:
        name: Register name string.

    Returns:
        A tuple containing:
        (address, dataType)

        address: Address value corresponding to the register name.
        dataType: Data type value corresponding to the register names.

    Raises:
        TypeError: name is not a string.
        LJMError: An error was returned from the LJM library call.

    """
    if not isinstance(name, str):
        raise TypeError("Expected a string instead of " + str(type(name)) + ".")
    cAddr = ctypes.c_int32(0)
    cType = ctypes.c_int32(0)

    error = _staticLib.LJM_NameToAddress(name.encode("ascii"), ctypes.byref(cAddr), ctypes.byref(cType))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cAddr.value, cType.value


def addressesToTypes(numAddresses, aAddresses):
    """Takes a list of Modbus register addresses and returns their data
    types.

    Args:
        numAddresses: The number of addresses you want the data types
            of.
        address: A list of the Modbus register addresses you want the
            data types of.

    Returns:
        A list of data types corresponding to the address list.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    cNumAddrs = ctypes.c_int32(numAddresses)
    cAddrs = _convertListToCtypeArray(aAddresses, ctypes.c_int32)
    cTypes = (ctypes.c_int32*numAddresses)()

    error = _staticLib.LJM_AddressesToTypes(cNumAddrs, ctypes.byref(cAddrs), ctypes.byref(cTypes))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return _convertCtypeArrayToList(cTypes)


def addressToType(address):
    """Takes a Modbus register address and returns its data type.

    Args:
        address: The Modbus register address you want the data type of.

    Returns:
        The data type of the address.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    cAddr = ctypes.c_int32(address)
    cType = ctypes.c_int32(0)

    error = _staticLib.LJM_AddressToType(cAddr, ctypes.byref(cType))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cType.value


def lookupConstantValue(scope, constantName):
    """Takes a register name or other scope and a constant name, and
    returns the constant value.

    Args:
        scope: The register name or other scope string to search within.
        constantName: The name of the constant string to search for.

    Returns:
        The constant value from the given scope, if found.

    Raises:
        TypeError: scope or constantName is not a string.
        LJMError: An error was returned from the LJM library call.

    """
    if not isinstance(scope, str):
        raise TypeError("Expected a string instead of " + str(type(scope)) + ".")
    if not isinstance(constantName, str):
        raise TypeError("Expected a string instead of " + str(type(constantName)) + ".")
    cConstVal = ctypes.c_double(0)

    error = _staticLib.LJM_LookupConstantValue(scope.encode("ascii"), constantName.encode("ascii"), ctypes.byref(cConstVal))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cConstVal.value


def lookupConstantName(scope, constantValue):
    """Takes a register name or other scope and a value, and returns the
    name of that value.

    Args:
        scope: The register name or other scope string to search within.
        constantName: The constant value integer to search for.

    Returns:
        The constant name from the given scope, if found.

    Raises:
        TypeError: scope is not a string.
        LJMError: An error was returned from the LJM library call.

    """
    if not isinstance(scope, str):
        raise TypeError("Expected a string instead of " + str(type(scope)) + ".")
    cConstVal = ctypes.c_double(constantValue)
    cConstName = ("\0"*constants.MAX_NAME_SIZE).encode("ascii")

    error = _staticLib.LJM_LookupConstantName(scope.encode("ascii"), cConstVal, cConstName)
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return _decodeASCII(cConstName)


def errorToString(errorCode):
    """Returns the the name of an error code.

    Args:
        errorCode: The error code to look up.

    Returns:
        The error name string.

    Note:
        If the constants file that has been loaded does not contain
        errorCode, this returns a message saying so. If the constants
        file could not be opened, this returns a string saying so and
        where that constants file was expected to be.

    """
    cErr = ctypes.c_int32(errorCode)
    errStr = ("\0"*constants.MAX_NAME_SIZE).encode("ascii")

    _staticLib.LJM_ErrorToString(cErr, errStr)

    return _decodeASCII(errStr)


def loadConstants():
    """Manually loads or reloads the constants files associated with
    the errorToString and namesToAddresses functions.

    Note:
        This step is handled automatically. This function does not
        need to be called before either errorToString or
        namesToAddresses.

    """
    _staticLib.LJM_LoadConstants()


def loadConstantsFromFile(fileName):
    """Loads the constants file from the given file name. Alias for
    executing:
        writeLibraryConfigStringS(labjack.ljm.constants.CONSTANTS_FILE,
            fileName)

    Args:
        fileName: A file name string using relative or absolute path
            to pass to writeLibraryConfigStringS.

    Raises:
        TypeError: filePath is not a string.
        LJMError: An error was returned from the LJM library call.

    """
    if not isinstance(fileName, str):
        raise TypeError("Expected a string instead of " + str(type(fileName)) + ".")

    error = _staticLib.LJM_LoadConstantsFromFile(fileName.encode("ascii"))
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def loadConstantsFromString(jsonString):
    """Parses jsonString as the constants file and loads it.

    Args:
        jsonString: A JSON string containing a "registers" array and/or
            an "errors" array.

    Raises:
        TypeError: jsonString is not a string.
        LJMError: An error was returned from the LJM library call.

    Note:
        If the JSON string does not contain a "registers" array, the
        Modbus-related constants are not affected. Similarly, if the
        JSON string does not contain an "errors" array, the errorcode-
        related constants are not affected.

    """
    if not isinstance(jsonString, str):
        raise TypeError("Expected a string instead of " + str(type(jsonString)) + ".")

    error = _staticLib.LJM_LoadConstantsFromString(jsonString.encode("ascii"))
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def tcVoltsToTemp(tcType, tcVolts, cjTempK):
    """Converts thermocouple voltage to a temperature.

    Args:
        tcType: The thermocouple type. See "Thermocouple Type constants"
            in labjack.ljm.constants (ttX).
        tcVolts: The voltage reported by the thermocouple.
        cjTempK: The cold junction temperature in degrees Kelvin.

    Returns:
        The calculated temperature in degrees Kelvin.

    Raises:
        LJMError: An error was returned from the LJM library call.

    Notes:
        B-type measurements below ~373 degrees Kelvin or ~0.04
        millivolts (at a cold junction junction temperature of 273.15
        degrees Kelvin) may be inaccurate.

    """
    cTCType = ctypes.c_int32(tcType)
    cTCVolts = ctypes.c_double(tcVolts)
    cCJTempK = ctypes.c_double(cjTempK)
    cTCTempK = ctypes.c_double(0)

    error = _staticLib.LJM_TCVoltsToTemp(cTCType, cTCVolts, cCJTempK, ctypes.byref(cTCTempK))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cTCTempK.value


def float32ToByteArray(aFLOAT32, registerOffset=0, numFLOAT32=None, aBytes=None):
    """Converts a list of values from 32-bit floats to bytes
    (big-endian).

    Args:
        aFLOAT32: The list of 32-bit float values to be converted.
        registerOffset: The register offset to put the converted values
            in aBytes. Default is 0.
        numFLOAT32: The number of values to convert. Default is None
            and will be set to the list length of aFLOAT32.
        aBytes: Byte list to pass. It should be at least
            registerOffset*2 + numFLOAT32*4 in size. Default is None,
            which creates a list of the correct size filled with zeros.

    Returns:
        A list of converted values in byte form.

    """
    cFloats = _convertListToCtypeArray(aFLOAT32, ctypes.c_float)
    cRegOffset = ctypes.c_int32(registerOffset)
    if numFLOAT32 is None:
        numFLOAT32 = len(cFloats)
    cNumFloat = ctypes.c_int32(numFLOAT32)
    numBytes = numFLOAT32*4 + registerOffset*2
    if aBytes is None:
        aBytes = [0]*numBytes
    cUbytes = _convertListToCtypeArray(aBytes, ctypes.c_ubyte)

    _staticLib.LJM_FLOAT32ToByteArray(ctypes.byref(cFloats), cRegOffset, cNumFloat, ctypes.byref(cUbytes))

    return _convertCtypeArrayToList(cUbytes)


def byteArrayToFLOAT32(aBytes, registerOffset=0, numFLOAT32=None, aFLOAT32=None):
    """Converts a list of values from bytes (big-endian) to 32-bit
    floats.

    Args:
        aBytes: The bytes to be converted.
        registerOffset: The register offset to get the values from in
            aBytes. Default is 0.
        numFLOAT32: The number of 32-bit float values to convert.
            Default is None, and will be the length of the aBytes list
            divided by 4.
        aFLOAT32: Float list to pass. It should be at least numFLOAT32
            in size.  Default is None, which creates a list of the
            correct size filled with zeros.

    Returns:
        A list of converted values in float form.

    """
    cUbytes = _convertListToCtypeArray(aBytes, ctypes.c_ubyte)
    cRegOffset = ctypes.c_int32(registerOffset)
    maxNum = int((len(cUbytes)-registerOffset*2)/4)
    if numFLOAT32 is None:
        numFLOAT32 = maxNum
    cNumFloat = ctypes.c_int32(numFLOAT32)
    if aFLOAT32 is None:
        aFLOAT32 = [0]*numFLOAT32
    cFloats = _convertListToCtypeArray(aFLOAT32, ctypes.c_float)

    _staticLib.LJM_ByteArrayToFLOAT32(ctypes.byref(cUbytes), cRegOffset, cNumFloat, ctypes.byref(cFloats))

    return _convertCtypeArrayToList(cFloats)


def uint16ToByteArray(aUINT16, registerOffset=0, numUINT16=None, aBytes=None):
    """Converts a list of values from 16-bit unsigned integers to bytes
    (big-endian).

    Args:
        aUINT16: The list of 16-bit unsigned integer values to be
            converted.
        registerOffset: The register offset to put the converted values
            in aBytes. Default is 0.
        numUINT16: The number of values to convert. Default is None
            and will be set to the list length of aUINT16.
        aBytes: Byte list to pass. It should be at least
            registerOffset*2 + numUINT16*2 in size. Default is None,
            which creates a list of the correct size filled with zeros.

    Returns:
        A list of converted values in byte form.

    """
    cUint16s = _convertListToCtypeArray(aUINT16, ctypes.c_uint16)
    cRegOffset = ctypes.c_int32(registerOffset)
    if numUINT16 is None:
        numUINT16 = len(cUint16s)
    cNumUint16 = ctypes.c_int32(numUINT16)
    numBytes = numUINT16*2 + registerOffset*2
    if aBytes is None:
        aBytes = [0]*numBytes
    cUbytes = _convertListToCtypeArray(aBytes, ctypes.c_ubyte)

    _staticLib.LJM_UINT16ToByteArray(ctypes.byref(cUint16s), cRegOffset, cNumUint16, ctypes.byref(cUbytes))

    return _convertCtypeArrayToList(cUbytes)


def byteArrayToUINT16(aBytes, registerOffset=0, numUINT16=None, aUINT16=None):
    """Converts a list of values from bytes (big-endian) to 16-bit
    unsigned integers.

    Args:
        aBytes: The bytes to be converted.
        registerOffset: The register offset to get the values from in
            aBytes. Default is 0.
        numUINT16: The number of 16-bit unsigned integer values to
            convert. Default is None, and will be the length of the
            aBytes list divided by 2.
        aUINT16: 16-bit unsigned integer list to pass. It should be
            at least numUINT16 in size. Default is None, which
            creates a list of the correct size filled with zeros.

    Returns:
        A list of converted values in 16-bit unsigned integer form.

    """
    cUbytes = _convertListToCtypeArray(aBytes, ctypes.c_ubyte)
    cRegOffset = ctypes.c_int32(registerOffset)
    maxNum = int((len(cUbytes)-registerOffset*2)/2)
    if numUINT16 is None:
        numUINT16 = maxNum
    cNumUint16 = ctypes.c_int32(numUINT16)
    if aUINT16 is None:
        aUINT16 = [0]*numUINT16
    cUint16s = _convertListToCtypeArray(aUINT16, ctypes.c_uint16)

    _staticLib.LJM_ByteArrayToUINT16(ctypes.byref(cUbytes), cRegOffset, cNumUint16, ctypes.byref(cUint16s))

    return _convertCtypeArrayToList(cUint16s)


def uint32ToByteArray(aUINT32, registerOffset=0, numUINT32=None, aBytes=None):
    """Converts a list of values from 32-bit unsigned integers to bytes
    (big-endian).

    Args:
        aUINT32: The list of 32-bit unsigned integer values to be
            converted.
        registerOffset: The register offset to put the converted values
            in aBytes. Default is 0.
        numUINT32: The number of values to convert. Default is None
            and will be set to the list length of aUINT32.
        aBytes: Byte list to pass. It should be at least
            registerOffset*2 + numUINT32*4 in size. Default is None,
            which creates a list of the correct size filled with
            zeros.

    Returns:
        A list of converted values in byte form.

    """
    cUint32s = _convertListToCtypeArray(aUINT32, ctypes.c_uint32)
    cRegOffset = ctypes.c_int32(registerOffset)
    if numUINT32 is None:
        numUINT32 = len(cUint32s)
    cNumUint32 = ctypes.c_int32(numUINT32)
    numBytes = numUINT32*4 + registerOffset*2
    if aBytes is None:
        aBytes = [0]*numBytes
    cUbytes = _convertListToCtypeArray(aBytes, ctypes.c_ubyte)

    _staticLib.LJM_UINT32ToByteArray(ctypes.byref(cUint32s), cRegOffset, cNumUint32, ctypes.byref(cUbytes))

    return _convertCtypeArrayToList(cUbytes)


def byteArrayToUINT32(aBytes, registerOffset=0, numUINT32=None, aUINT32=None):
    """Converts a list of values from bytes (big-endian) to 32-bit
    unsigned integers.

    Args:
        aBytes: The bytes to be converted.
        registerOffset: The register offset to get the values from in
            aBytes. Default is 0.
        numUINT32: The number of 32-bit unsigned integer values to
            convert. Default is None, and will be the length of the
            aBytes list divided by 4.
        aUINT32: 32-bit unsigned integer list to pass. It should be
            at least numUINT32 in size. Default is None, which
            creates a list of the correct size filled with zeros.

    Returns:
        A List of converted values in 32-bit unsigned integer
        form.

    """
    cUbytes = _convertListToCtypeArray(aBytes, ctypes.c_ubyte)
    cRegOffset = ctypes.c_int32(registerOffset)
    maxNum = int((len(cUbytes)-registerOffset*2)/4)
    if numUINT32 is None:
        numUINT32 = maxNum
    cNumUint32 = ctypes.c_int32(numUINT32)
    if aUINT32 is None:
        aUINT32 = [0]*numUINT32
    cUint32s = _convertListToCtypeArray(aUINT32, ctypes.c_uint32)

    _staticLib.LJM_ByteArrayToUINT32(ctypes.byref(cUbytes), cRegOffset, cNumUint32, ctypes.byref(cUint32s))

    return _convertCtypeArrayToList(cUint32s)


def int32ToByteArray(aINT32, registerOffset=0, numINT32=None, aBytes=None):
    """Converts a list of values from 32-bit signed integers to bytes
    (big-endian).

    Args:
        aINT32: The list of 32-bit signed integer values to be
            converted.
        registerOffset: The register offset to put the converted values
            in aBytes. Default is 0.
        numINT32: The number of values to convert. Default is None and
            will be set to the list length of aINT32.
        aBytes: Byte list to pass. It should be at least
            registerOffset*2 + numINT32*4 in size. Default is None,
            which creates a byte list of the correct size filled with
            zeros.

    Returns:
        A list of converted values in byte form.

    """
    cInt32s = _convertListToCtypeArray(aINT32, ctypes.c_int32)
    cRegOffset = ctypes.c_int32(registerOffset)
    if numINT32 is None:
        numINT32 = len(cInt32s)
    cNumInt32 = ctypes.c_int32(numINT32)
    numBytes = numINT32*4 + registerOffset*2
    if aBytes is None:
        aBytes = [0]*numBytes
    cUbytes = _convertListToCtypeArray(aBytes, ctypes.c_ubyte)

    _staticLib.LJM_INT32ToByteArray(ctypes.byref(cInt32s), cRegOffset, cNumInt32, ctypes.byref(cUbytes))

    return _convertCtypeArrayToList(cUbytes)


def byteArrayToINT32(aBytes, registerOffset=0, numINT32=None, aINT32=None):
    """Converts a list of values from bytes (big-endian) to 32-bit
    signed integers.

    Args:
        aBytes: The bytes to be converted.
        registerOffset: The register offset to get the values from in
            aBytes. Default is 0.
        numINT32: The number of 32-bit signed integer values to convert.
            Default is None, and will be the length of the aBytes list
            divided by 4.
        aINT32: 32-bit signed integer list to pass. It should be
            at least numINT32 in size. Default is None, which
            creates a list of the correct size filled with zeros.

    Returns:
        A List of converted values in 32-bit signed integer form.

    """
    cUbytes = _convertListToCtypeArray(aBytes, ctypes.c_ubyte)
    cRegOffset = ctypes.c_int32(registerOffset)
    maxNum = int((len(cUbytes)-registerOffset*2)/4)
    if numINT32 is None:
        numINT32 = maxNum
    cNumInt32 = ctypes.c_int32(numINT32)
    if aINT32 is None:
        aINT32 = [0]*numINT32
    cInt32s = _convertListToCtypeArray(aINT32, ctypes.c_int32)

    _staticLib.LJM_ByteArrayToINT32(ctypes.byref(cUbytes), cRegOffset, cNumInt32, ctypes.byref(cInt32s))

    return _convertCtypeArrayToList(cInt32s)


def numberToIP(number):
    """Takes an integer representing an IPv4 address and returns the
    corresponding decimal-dot IPv4 address as a string.

    Args:
        number: The numerical representation of an IP address to be
            converted to a string representation.

    Returns:
        The converted string representation of the IP address.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    cNum = ctypes.c_uint32(number)
    ipv4String = ("\0"*constants.IPv4_STRING_SIZE).encode("ascii")

    error = _staticLib.LJM_NumberToIP(cNum, ipv4String)
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return _decodeASCII(ipv4String)


def ipToNumber(ipv4String):
    """Takes a decimal-dot IPv4 string representing an IPv4 address and
    returns the corresponding integer version of the address.

    Args:
        ipv4String: The string representation of the IP address to be
            converted to a numerical representation.

    Returns:
        The numerical representation of ipv4String.

    Raises:
        TypeError: ipv4String is not a string.
        LJMError: An error was returned from the LJM library call.

    """
    if not isinstance(ipv4String, str):
        raise TypeError("Expected a string instead of " + str(type(ipv4String)) + ".")
    if len(ipv4String) < constants.IPv4_STRING_SIZE:
        ipv4String += "\0"*(constants.IPv4_STRING_SIZE-len(ipv4String))
    cNum = ctypes.c_uint32(0)

    error = _staticLib.LJM_IPToNumber(ipv4String.encode("ascii"), ctypes.byref(cNum))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cNum.value


def numberToMAC(number):
    """Takes an integer representing a MAC address and outputs the
    corresponding hex-colon MAC address as a string.

    Args:
        number: The numerical representation of a MAC address to be
            converted to a string representation.

    Returns:
        The string representation of the MAC address after the
        completion of this function.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    cNum = ctypes.c_uint64(number)
    macString = ("\0"*constants.MAC_STRING_SIZE).encode("ascii")

    _staticLib.LJM_NumberToMAC.argtypes = [ctypes.c_uint64, ctypes.c_char_p]
    error = _staticLib.LJM_NumberToMAC(number, macString)
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return _decodeASCII(macString)


def macToNumber(macString):
    """Takes a hex-colon string representing a MAC address and outputs
    the corresponding integer version of the address.

    Args:
        macString: The string representation of the MAC address to be
            converted to a numerical representation.

    Returns:
        The numerical representation of macString.

    Raises:
        TypeError: macString is not a string.
        LJMError: An error was returned from the LJM library call.

    """
    if not isinstance(macString, str):
        raise TypeError("Expected a string instead of " + str(type(macString)) + ".")
    if len(macString) < constants.MAC_STRING_SIZE:
        macString += "\0"*(constants.MAC_STRING_SIZE-len(macString))
    cNum = ctypes.c_uint64(0)

    error = _staticLib.LJM_MACToNumber(macString.encode("ascii"), ctypes.byref(cNum))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cNum.value


def getHostTick():
    """Queries the host system's steady (monotonic) clock,
    preferentially with high precision.

    Returns:
        The current clock tick in microseconds.

    """
    _staticLib.LJM_GetHostTick.restype = ctypes.c_uint64
    return _staticLib.LJM_GetHostTick()


def getHostTick32Bit():
    """Queries the host system's steady (monotonic) clock,
    preferentially with high precision, but returns two 32-bit integers
    for the 64-bit clock tick.

    Returns:
        A tuple containing:
        (tickUpper, tickLower)

        tickUpper: The upper (most significant) 32 bits of the clock
            tick.
        tickLower: The lower (least significant) 32 bits of the clock
            tick.

    """
    cUpper = ctypes.c_uint32(0)
    cLower = ctypes.c_uint32(0)

    _staticLib.LJM_GetHostTick32Bit(ctypes.byref(cUpper), ctypes.byref(cLower))

    return cUpper.value, cLower.value


def startInterval(intervalHandle, microseconds):
    """Allocates memory for the given intervalHandle and begins a
    reoccurring interval timer. This function does not wait.

    Args:
        intervalHandle: The user-generated interval identifier.
        microseconds: The number of microseconds in the interval.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    cIntervalHandle = ctypes.c_int32(intervalHandle)
    cMicrosecs = ctypes.c_int32(microseconds)

    error = _staticLib.LJM_StartInterval(cIntervalHandle, cMicrosecs)
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def waitForNextInterval(intervalHandle):
    """Waits (blocks/sleeps) until the next interval occurs. If
    intervals are skipped, this function still waits until the next
    complete interval.

    Args:
        intervalHandle: The user-generated interval identifier.

    Returns:
        The number of skipped intervals.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    cIntervalHandle = ctypes.c_int32(intervalHandle)
    cSkipIntervals = ctypes.c_int32(0)

    error = _staticLib.LJM_WaitForNextInterval(cIntervalHandle, ctypes.byref(cSkipIntervals))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cSkipIntervals.value


def cleanInterval(intervalHandle):
    """Cleans/deallocates memory for the given intervalHandle.

    Args:
        intervalHandle: The user-generated interval identifier.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    cIntervalHandle = ctypes.c_int32(intervalHandle)

    error = _staticLib.LJM_CleanInterval(cIntervalHandle)
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def writeLibraryConfigS(parameter, value):
    """Writes/sets a library configuration/setting.

    Args:
        parameter: Name of the configuration value you want to set.
            Needs to be a string and is not case-sensitive.
        value: The config value.

    Raises:
        TypeError: parameter is not a string.
        LJMError: An error was returned from the LJM library call.

    """
    if isinstance(parameter, str) is False:
        raise TypeError("Expected a string instead of " + str(type(parameter)) + ".")
    cVal = ctypes.c_double(value)

    error = _staticLib.LJM_WriteLibraryConfigS(parameter.encode("ascii"), cVal)
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def writeLibraryConfigStringS(parameter, string):
    """Writes/sets a library configuration/setting.

    Args:
        parameter: Name of the configuration value you want to set.
            Needs to be a string and is not case-sensitive.
        string: The config value string. Must not be of size greater
            than labjack.ljm.constants.MAX_NAME_SIZE

    Raises:
        TypeError: parameter or string is not a string.
        LJMError: An error was returned from the LJM library call.

    """
    if not isinstance(parameter, str):
        raise TypeError("Expected a string instead of " + str(type(parameter)) + ".")
    if not isinstance(string, str):
        raise TypeError("Expected a string instead of " + str(type(string)) + ".")

    error = _staticLib.LJM_WriteLibraryConfigStringS(parameter.encode("ascii"), string.encode("ascii"))
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def readLibraryConfigS(parameter):
    """Reads a configuration/setting value from the library.

    Args:
        parameter: Name of the configuration value you want to read.
            Needs to be a string and is not case-sensitive.

    Returns:
        The read config value as a float.

    Raises:
        TypeError: parameter is not a string.
        LJMError: An error was returned from the LJM library call.

    """
    if not isinstance(parameter, str):
        raise TypeError("Expected a string instead of " + str(type(parameter)) + ".")
    cVal = ctypes.c_double(0)

    error = _staticLib.LJM_ReadLibraryConfigS(parameter.encode("ascii"), ctypes.byref(cVal))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cVal.value


def readLibraryConfigStringS(parameter):
    """Reads a configuration/setting string from the library.

    Args:
        parameter: Name of the configuration value you want to read.
            Needs to be a string and is not case-sensitive.

    Returns:
        The read config string.

    Raises:
        TypeError: parameter is not a string.
        LJMError: An error was returned from the LJM library call.

    """
    if not isinstance(parameter, str):
        raise TypeError("Expected a string instead of " + str(type(parameter)) + ".")
    outStr = ("\0"*constants.MAX_NAME_SIZE).encode("ascii")

    error = _staticLib.LJM_ReadLibraryConfigStringS(parameter.encode("ascii"), outStr)
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return _decodeASCII(outStr)


def loadConfigurationFile(fileName):
    """Reads a file in as the new LJM configurations.

    Args:
        fileName: A file name string using relative or absolute path.
            "default" maps to the default configuration file
            ljm_startup_config.json in the constants file location.

    Raises:
        TypeError: fileName is not a string.
        LJMError: An error was returned from the LJM library call.

    """
    if not isinstance(fileName, str):
        raise TypeError("Expected a string instead of " + str(type(fileName)) + ".")

    error = _staticLib.LJM_LoadConfigurationFile(fileName.encode("ascii"))
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def getSpecificIPsInfo():
    """Get information about whether the specific IPs file was parsed
    successfully.

    Returns:
        A tuple containing:
        (infoHandle, info)

        infoHandle: A handle to info that should be passed to cleanInfo
            after info has been read.
        info: A JSON string (allocated by LJM) describing the state of
            of the specific IPs. Semantics:
            {
                "errorCode": Integer LJME_ error code. 0 indicates no
                    error.
                "IPs": Array of strings - the presentation-format IPs.
                "message": Human-readable string description of
                    success/failure.
                "filePath": String absolute or relative file path.
                "invalidIPs": Array of strings - the unparsable lines.
            }

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    cInfoHandle = ctypes.c_int32(0)
    cInfo = ctypes.c_char_p()

    error = _staticLib.LJM_GetSpecificIPsInfo(ctypes.byref(cInfoHandle), ctypes.byref(cInfo))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cInfoHandle.value, _decodeASCII(cInfo.value)


def getDeepSearchInfo():
    """Get information about whether the Deep Search file was parsed
    successfully.

    Returns:
        A tuple containing:
        (infoHandle, info)

        infoHandle: A handle to Info that should be passed to cleanInfo
            after info has been read.
        info: A JSON string (allocated by LJM) describing the state of
            state of the Deep Search IPs. Semantics:
            {
                "errorCode": Integer LJME_ error code. 0 indicates no
                    error.
                "IPs": Array of strings - the presentation-format IPs.
                "message": Human-readable string description of
                    success/failure.
                "filePath": String absolute or relative file path.
                "invalidIPs": Array of strings - the unparsable lines.
            }

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    cInfoHandle = ctypes.c_int32(0)
    cInfo = ctypes.c_char_p()

    error = _staticLib.LJM_GetDeepSearchInfo(ctypes.byref(cInfoHandle), ctypes.byref(cInfo))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cInfoHandle.value, _decodeASCII(cInfo.value)


def log(level, string):
    """Sends a message of the specified level to the LJM debug logger.

    Args:
        level: The level to output the message at. See
            labjack.ljm.constants.DEBUG_LOG_LEVEL.
        string: The debug message to be written to the log file.

    Raises:
        TypeError: string parameter is not a string.
        LJMError: An error was returned from the LJM library call.

    Note: By default, DEBUG_LOG_MODE is to never log, so LJM does
        not output any log messages, even from this function.

    """
    cLev = ctypes.c_int32(level)
    if not isinstance(string, str):
        raise TypeError("Expected a string instead of " + str(type(string)) + ".")

    error = _staticLib.LJM_Log(cLev, string.encode("ascii"))
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def resetLog():
    """Clears all characters from the debug log file.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    error = _staticLib.LJM_ResetLog()
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def _convertListToCtypeArray(li, cType):
    """Returns a ctypes list converted from a normal list."""
    return (cType*len(li))(*li)


def _convertCtypeArrayToList(listCtype):
    """Returns a normal list from a ctypes list."""
    return listCtype[:]


def _decodeASCII(string):
    """Returns an ASCII decoded version of the null terminated string.
    Non ASCII characters are ignored."""
    return str(string.decode("ascii", "ignore").split("\0", 1)[0])
