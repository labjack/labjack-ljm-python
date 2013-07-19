"""
Cross-platform Python wrapper for the LJM library.

"""

from labjack.ljm import constants
from labjack.ljm import errorcodes
import ctypes


__version__ = "0.8.6"


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
            errorCodeStr = "LJM library error code " + str(self._errorCode) + " "
        return addrStr + errorCodeStr + self._errorString


def _loadLibrary():
    """Returns a ctypes pointer to the LJM library."""
    import sys

    try:
        libraryName = None
        try:
            if(sys.platform.startswith("win32") or sys.platform.startswith("cygwin")):
                #Windows
                libraryName = "LabJackM.dll"
            if(sys.platform.startswith("linux")):
                #Linux
                libraryName = "libLabJackM.so"
            if(sys.platform.startswith("darwin")):
                #Mac OS X
                libraryName = "libLabJackM.dylib"
            
            if libraryName is not None:
                if libraryName == "LabJackM.dll":
                    return ctypes.WinDLL(libraryName)
                else:
                    return ctypes.CDLL(libraryName)
        except Exception, e:
            raise LJMError(errorString = "Cannot load the LJM library " + str(libraryName) + ". " + str(e))

        #Unsupported operating system
        raise LJMError(errorString = "Cannot load the LJM library. Unsupported platform " + sys.platform + ".")
    except LJMError, ljme:
        print str(type(ljme)) + ": " + str(ljme)
        return None


_staticLib = _loadLibrary()


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
    for x in aNames:
        if not isinstance(x, str):
            raise TypeError("Expected a string list but found an item " + str(type(x)) + ".")
    cNames = _convertListToCtypeArray(aNames, ctypes.c_char_p)
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

    error = _staticLib.LJM_NameToAddress(name, ctypes.byref(cAddr), ctypes.byref(cType))
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

    error = _staticLib.LJM_AddressesToTypes(cNumAddrs, ctypes.byref(cAddrs), ctypes.byref(cTypes));
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


def listAll(deviceType, connectionType):
    """Scans for LabJack devices and returns lists describing the
    devices.

    Args:
        deviceType: An integer that filters which devices will be
            returned (labjack.ljm.constants.dtT7,
            labjack.ljm.constants.dtU3, etc.).
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
            devices, but only if the returned connection type is
            labjack.ljm.constants.ctTCP.

    Raises:
        LJMError: An error was returned from the LJM library call.

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
            ("LJM_dtT7", "LJM_dtU3", etc.). "LJM_dtANY" is allowed.
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
            devices, but only if the returned connection type is
            labjack.ljm.constants.ctTCP.

    Raises:
        TypeError: deviceType or connectionType are not strings.
        LJMError: An error was returned from the LJM library call.

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

    error = _staticLib.LJM_ListAllS(deviceType, connectionType, ctypes.byref(cNumFound), ctypes.byref(cDevTypes), ctypes.byref(cConnTypes), ctypes.byref(cSerNums), ctypes.byref(cIPAddrs))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    numFound = cNumFound.value
    return numFound, _convertCtypeArrayToList(cDevTypes[0:numFound]), _convertCtypeArrayToList(cConnTypes[0:numFound]), _convertCtypeArrayToList(cSerNums[0:numFound]), _convertCtypeArrayToList(cIPAddrs[0:numFound])


def openS(deviceType="ANY", connectionType="ANY", identifier="ANY"):
    """Opens a LabJack device, and returns the device handle.

    Args:
        deviceType: A string containing the type of the device to be
            connected, optionally prepended by "LJM_dt". Possible values
            include "ANY", "T7", and "DIGIT".
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

    Notes:
        Args are not case-sensitive, and empty strings indicate the
        same thing as "LJM_xxANY".

    """
    if not isinstance(deviceType, str):
        raise TypeError("Expected a string instead of " + str(type(deviceType)) + ".")
    if not isinstance(connectionType, str):
        raise TypeError("Expected a string instead of " + str(type(connectionType)) + ".")
    identifier = str(identifier)
    cHandle = ctypes.c_int32(0)

    error = _staticLib.LJM_OpenS(deviceType, connectionType, identifier, ctypes.byref(cHandle))
    if error != errorcodes.NOERROR:
       raise LJMError(error)

    return cHandle.value


def open(deviceType=0, connectionType=0, identifier="ANY"):
    """Opens a LabJack device, and returns the device handle.

    Args:
        deviceType: An integer containing the type of the device to be
            connected (labjack.ljm.constants.dtT7,
            labjack.ljm.constants.dtU3, labjack.ljm.constants.dtANY,
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

    error = _staticLib.LJM_Open(cDev, cConn, identifier, ctypes.byref(cHandle))
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
            address, or labjack.ljm.constants.NO_IP_ADDRESS if the
            device does not support Ethernet/TCP.  Use the numberToIP
            function to convert this value to a string.
        port: The port the device is connected on via Ethernet/TCP, or
            the pipe the device is connected on via USB.
        maxBytesPerMB: The maximum packet size in number of bytes that
            can be sent or received from this device. Note that this
            can change, depending on connection and device type.

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


def resetConnection(handle):
    """Manually resets the connection associated with handle.

    Args:
        handle: A valid handle to an open device.

    Raises:
        LJMError: An error was returned from the LJM library call.

    Note:
        This function will not necessarily always exist. It will
        eventually be taken care of automatically. In other words, don't
        use this function. :)

    """
    error = _staticLib.LJM_ResetConnection(handle);
    if error != errorcodes.NOERROR:
        raise LJMError(error)


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
    errStr = "\0"*constants.MAX_NAME_SIZE

    _staticLib.LJM_ErrorToString(cErr, errStr)

    return errStr.split("\0", 1)[0]


def loadConstants():
    """Manually loads or reloads the constants files associated with
    the errorToString and namesToAddresses functions.

    Note:
        This step is handled automatically. This function does not
        need to be called before either errorToString or
        namesToAddresses.

    """
    _staticLib.LJM_LoadConstants()


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


def eWriteAddress(handle, address, dataType, value):
    """Performs Modbus operations that writes a value to a device.

    Args:
        handle: A valid handle to an open device.
        address: Register address to write.
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
        address: Register address to read.
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
        name: Register name (string) to write.
        value: The value to write.

    Raises:
        TypeError: name is not a string.
        LJMError: An error was returned from the LJM library call.

    """
    if not isinstance(name, str):
        raise TypeError("Expected a string instead of " + str(type(name)) + ".")
    cVal = ctypes.c_double(value)

    error = _staticLib.LJM_eWriteName(handle, name, cVal)
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def eReadName(handle, name):
    """Performs Modbus operations that reads a value from a device.

    Args:
        handle: A valid handle to an open device.
        name: Register name (string) to read.

    Returns:
        The read value.

    Raises:
        TypeError: name is not a string.
        LJMError: An error was returned from the LJM library call.

    """
    if not isinstance(name, str):
        raise TypeError("Expected a string instead of " + str(type(name)) + ".")
    cVal = ctypes.c_double(0)

    error = _staticLib.LJM_eReadName(handle, name, ctypes.byref(cVal))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cVal.value


def eReadAddresses(handle, numFrames, aAddresses, aDataTypes):
    """Performs Modbus operations that reads values from a device.

    Args:
        handle: A valid handle to an open device.
        numFrames: The total number of reads to perform.
        aAddresses: List of register addresses to read. This list needs
            to be at least size numFrames.
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
        aNames: List of register names (strings) to read. This list
            needs to be at least size numFrames.

    Returns:
        A list of read values.

    Raises:
        TypeError: aNames is not a list of strings.
        LJMError: An error was returned from the LJM library call.

    """
    cNumFrames = ctypes.c_int32(numFrames)
    for x in aNames:
        if not isinstance(x, str):
            raise TypeError("Expected a string list but found an item " + str(type(x)) + ".")
    cNames = _convertListToCtypeArray(aNames, ctypes.c_char_p)
    cVals =  (ctypes.c_double*numFrames)()
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
        aAddresses: List of register addresses to write. This list needs
            to be at least size numFrames.
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
        aNames: List of register names (strings) to write. This list
            needs to be at least size numFrames.
        aValues: List of values to write. This list needs to be at least
            size numFrames.

    Raises:
        TypeError: aNames is not a list of strings.
        LJMError: An error was returned from the LJM library call.

    """
    cNumFrames = ctypes.c_int32(numFrames)
    for x in aNames:
        if not isinstance(x, str):
            raise TypeError("Expected a string list but found an item " + str(type(x)) + ".")
    cNames = _convertListToCtypeArray(aNames, ctypes.c_char_p)
    cVals = _convertListToCtypeArray(aValues, ctypes.c_double)
    cErrorAddr = ctypes.c_int32(-1)

    error = _staticLib.LJM_eWriteNames(handle, cNumFrames, ctypes.byref(cNames), ctypes.byref(cVals), ctypes.byref(cErrorAddr))
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
        aAddresses: List of register addresses to write. This list needs
            to be at least size numFrames.
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
        aNames: List of register names (strings) to write/read. This
            list needs to be at least size numFrames.
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
    for x in aNames:
        if not isinstance(x, str):
            raise TypeError("Expected a string list but found an item " + str(type(x)) + ".")
    cNames = _convertListToCtypeArray(aNames, ctypes.c_char_p)
    cWrites = _convertListToCtypeArray(aWrites, ctypes.c_int32)
    cNumVals = _convertListToCtypeArray(aNumValues, ctypes.c_int32)
    cVals = _convertListToCtypeArray(aValues, ctypes.c_double)
    cErrorAddr = ctypes.c_int32(-1)

    error = _staticLib.LJM_eNames(handle, cNumFrames, ctypes.byref(cNames), ctypes.byref(cWrites), ctypes.byref(cNumVals), ctypes.byref(cVals), ctypes.byref(cErrorAddr))
    if error != errorcodes.NOERROR:
        raise LJMError(error, cErrorAddr.value)

    return _convertCtypeArrayToList(cVals)


_g_eStreamDataSize = {}
def eStreamStart(handle, scansPerRead, numAddresses, aScanList, scanRate):
    """Initializes a stream object and begins streaming. This includes
       creating a buffer in LJM that collects data from the device.

    Args:
        handle: A valid handle to an open device.
        scansPerRead: Number of scans returned by each call to the
            eStreamRead function. This is not tied to the maximum packet
            size for the device.
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

    error = _staticLib.LJM_eStreamStart(handle, cSPR, cNumAddrs, ctypes.byref(cSL_p), ctypes.byref(cScanRate))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    _g_eStreamDataSize[handle] = scansPerRead*numAddresses
    return cScanRate.value


def eStreamRead(handle):
    """Returns data from an initialized and running LJM stream buffer.
    Waits for data to become available, if necessary.

    Args:
        handle: A valid handle to an open device.

    Returns:
        A tuple containing:
        (aData, numSkippedScans, deviceScanBacklog, ljmScanBackLog)

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
    #May need to change to optimize
    if handle not in _g_eStreamDataSize:
        raise LJMError(errorString = "Streaming has not been started for the given handle. Please call eStreamStart first.")
    cData = (ctypes.c_double*_g_eStreamDataSize[handle])()
    cD_SBL = ctypes.c_int32(0)
    cLJM_SBL = ctypes.c_int32(0)

    error = _staticLib.LJM_eStreamRead(handle, ctypes.byref(cData), ctypes.byref(cD_SBL), ctypes.byref(cLJM_SBL));
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return _convertCtypeArrayToList(cData), cD_SBL.value, cLJM_SBL.value


def eStreamStop(handle):
    """Stops the LJM library from streaming any more data from the
    device, while leaving any collected data in the LJM library's
    buffer to be read.

    Args:
        handle: A valid handle to an open device.

    Raises:
        LJMError: An error was returned from the LJM library call.

    """
    error = _staticLib.LJM_eStreamStop(handle)
    if error != errorcodes.NOERROR:
        raise LJMError(error)
    if handle in _g_eStreamDataSize:
        _g_eStreamDataSize[handle]


def eReadString(handle, name):
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
    outStr = "\0"*constants.STRING_ALLOCATION_SIZE

    error = _staticLib.LJM_eReadString(handle, name, outStr);
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return outStr.split("\0", 1)[0]


def eWriteString(handle, name, string):
    """Writes a string to a device.

    Args:
        handle: A valid handle to an open device.
        name: The string name of a register to write.

    Raises:
        TypeError: name is not a string.
        LJMError: An error was returned from the LJM library call.

    Note: This is a convenience function for eNames.

    """
    if not isinstance(name, str):
        raise TypeError("Expected a string instead of " + str(type(name)) + ".")
    if not isinstance(string, str):
        raise TypeError("Expected a string instead of " + str(type(string)) + ".")

    error = _staticLib.LJM_eWriteString(handle, name, string);
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def float32ToByteArray(aFLOAT32, registerOffset=0, numFLOAT32=None, aBytes=None):
    """Converts a list of values from 32-bit floats to bytes, performing
    automatic endian conversions if necessary.

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
    """Converts a list of values from bytes to 32-bit floats, performing
    automatic endian conversions if necessary.

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
    """Converts a list of values from 16-bit unsigned integers to bytes,
    performing automatic endian conversions if necessary.

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
    """Converts a list of values from bytes to 16-bit unsigned integers,
    performing automatic endian conversions if necessary.

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
    """Converts a list of values from 32-bit unsigned integers to bytes,
    performing automatic endian conversions if necessary.

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
    """Converts a list of values from bytes to 32-bit unsigned integers,
    performing automatic endian conversions if necessary.

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
    """Converts a list of values from 32-bit signed integers to bytes,
    performing automatic endian conversions if necessary.

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
    """Converts a list of values from bytes to 32-bit signed integers,
    performing automatic endian conversions if necessary.

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
    ipv4String = "\0"*constants.IPv4_STRING_SIZE

    error = _staticLib.LJM_NumberToIP(cNum, ipv4String)
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return ipv4String.split("\0", 1)[0]


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

    error = _staticLib.LJM_IPToNumber(ipv4String, ctypes.byref(cNum));
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
    macString = "\0"*constants.MAC_STRING_SIZE

    _staticLib.LJM_NumberToMAC.argtypes = [ctypes.c_uint64, ctypes.c_char_p]
    error = _staticLib.LJM_NumberToMAC(number, macString)
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return macString.split("\0", 1)[0]


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

    error = _staticLib.LJM_MACToNumber(macString, ctypes.byref(cNum))
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return cNum.value


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

    error = _staticLib.LJM_WriteLibraryConfigS(parameter, cVal)
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

    error = _staticLib.LJM_WriteLibraryConfigStringS(parameter, string)
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

    error = _staticLib.LJM_ReadLibraryConfigS(parameter, ctypes.byref(cVal))
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
    outStr = "\0"*constants.MAX_NAME_SIZE

    error = _staticLib.LJM_ReadLibraryConfigStringS(parameter, outStr)
    if error != errorcodes.NOERROR:
        raise LJMError(error)

    return outStr.split("\0", 1)[0]


def log(level, string):
    """Outputs a message to the log file at the specified level.

    Args:
        level: The log level to output the message at.
            TODO: Define log levels
        string: The message string to be written to the log file.

    Raises:
        TypeError: string parameter is not a string.
        LJMError: An error was returned from the LJM library call.

    Note: This function may be temporary.

    """
    cLev = ctypes.c_int32(level)
    if not isinstance(string, str):
        raise TypeError("Expected a string instead of " + str(type(string)) + ".")

    error = _staticLib.LJM_Log(cLev, string)
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def resetLog():
    """Clears the log file.

    Raises:
        LJMError: An error was returned from the LJM library call.

    Note: This function may be temporary.

    """
    error = _staticLib.LJM_ResetLog()
    if error != errorcodes.NOERROR:
        raise LJMError(error)


def _convertListToCtypeArray(li, cType):
    """Returns a ctypes list converted from a normal list."""
    return (cType*len(li))(*li)


def _convertCtypeArrayToList(listCtype):
    """Returns a normal list from a ctypes list."""
    return [i for i in listCtype]
