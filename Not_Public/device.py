from labjack import ljm

class Device(object):
    def __init__(self, deviceType="LJM_dtANY", connectionType="LJM_ctANY", identifier="LJM_idANY"):
        self.handle = None
        self.deviceType = None
        self.connectionType = None
        self.serialNumber = None
        self.ipAddress = None
        self.port = None
        self.maxBytesPerMB = None

        if isinstance(deviceType, str) and isinstance(connectionType, str):
            self._openS(deviceType, connectionType, identifier)
        elif isinstance(deviceType, int) and isinstance(connectionType, int):
            self._open(deviceType, connectionType, identifier)
        else:
            raise TypeError("deviceType and connectionType need to both be a string or integer, not " + str(type(connectionType)) + "and " + str(type(connectionType)))
            
        self.getHandleInfo()

    def _openS(self, deviceType, connectionType, identifier):
        self.handle = ljm.openS(deviceType, connectionType, identifier)

    def _open(self, deviceType, connectionType, identifier):
        self.handle = ljm.open(deviceType, connectionType, identifier)[0]

    def openS(self, deviceType="LJM_dtANY", connectionType="LJM_ctANY", identifier="LJM_idANY"):
        """Opens a LabJack device, and saves the device handle.
    
        Args:
            deviceType: A string containing the type of the device to be
                connected ("LJM_dtT7", "LJM_dtU3", "LJM_dtANY", etc.).
            ConnectionType: A string containing the type of connection
                desired ("LJM_ctUSB", "LJM_ctTCP", "LJM_ctANY", etc.).
            Identifier: A string identifying the device to connect to or
                "LJM_idANY". This can be a serial number, IP address, or
                device name. Device names may not contain periods.

        Raises:
            TypeError: deviceType or connectionType are not strings.
            LJMError: An error was returned from the LJM library call.
    
        Notes:
            Args are not case-sensitive, and empty strings indicate the
            same thing as "LJM_xxANY".
    
        """
        self._openS(deviceType, connectionType, identifier)


    def open(self, deviceType=0, connectionType=0, identifier="LJM_idANY"):
        """Opens a LabJack device, and saves the device handle.
    
        Args:
            deviceType: An integer containing the type of the device to be
                connected (constants.dtT7, constants.dtU3, constants.dtANY,
                etc.).
            connectionType: An integer containing the type of connection
                desired (constants.ctUSB, constants.ctTCP, constants.ctANY,
                etc.).
            Identifier: A string identifying the device to connect to or
                "LJM_idANY". This can be a serial number, IP address, or
                device name. Device names may not contain periods.
    
        Raises:
            TypeError: deviceType or connectionType are not integers.
            LJMError: An error was returned from the LJM library call.
    
        Notes:
            Args are not case-sensitive.
            Empty strings indicate the same thing as "LJM_xxANY".
    
        """
        self._open(deviceType, connectionType, identifier)[0]
    
    
    def getHandleInfo(self):
        """Saves and returns the device handle's details.

        Args:
            handle: A valid handle to an open device.

        Returns:
            A tuple containing:
            (deviceType, connectionType, serialNumber, ipAddress, port,
            maxBytesPerMB)

            deviceType: The device type corresponding to an integer
                constant such as constants.dtT7.
            connectionType: The output device type corresponding to an
                integer constant such as constants.ctUSB
            serialNumber: The serial number of the device.
            ipAddress: The integer representation of the device's IP
                address, or constants.NO_IP_ADDRESS if the device does not
                support Ethernet/TCP.  Use the numberToIP function to
                convert this value to a string.
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
        info = ljm.getHandleInfo(self.handle)
        
        self.deviceType = info[0]
        self.connectionType = info[1]
        self.serialNumber = info[2]
        self.ipAddress = info[3]
        self.port = info[4]
        self.maxBytesPerMB = info[5]

        return info


    def mbfbComm(self, unitID, aMBFB):
        """Sends a Modbus Feedback command and receives a Feedback response,
        and parses the response for obvious errors. This function adds its
        own Transaction ID to the command.
    
        Args:
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
        return ljm.mbfbComm(self.handle, unitID, aMBFB)

    
    def resetConnection(self):
        """Manually resets the connection.
    
        Raises:
            LJMError: An error was returned from the LJM library call.
    
        Note:
            This function will not necessarily always exist. It will
            eventually be taken care of automatically. In other words, don't
            use this function. :)
    
        """
        ljm.resetConnection(self.handle)

    
    def close(self):
        """Closes the connection to the device.
    
        Raises:
            LJMError: An error was returned from the LJM library call.
    
        """
        ljm.close(self.handle)
    
    
    def writeRaw(self, data, numBytes=None):
        """Sends an unaltered data packet to a device.
    
        Args:
            data: The byte list/packet to send.
            numBytes: The number of bytes to send.  Default is None and will
                automaticcally send all the bytes in the data list.
    
        Raises:
            LJMError: An error was returned from the LJM library call.
    
        """
        ljm.writeRaw(self.handle, data, numBytes)
    
    
    def readRaw(self, numBytes):
        """Reads an unaltered data packet from a device.
    
        Args:
            numBytes: The number of bytes to receive.
    
        Returns:
            A list that is the read byte packet. It is length numBytes.
    
        Raises:
            LJMError: An error was returned from the LJM library call.
    
        """
        return ljm.readRaw(self.handle, numBytes)


    def eWriteAddress(self, address, dataType, value):
        """Performs Modbus operations that writes a value to a device.

        Args:
            address: Register address to write.
            dataTypes: The data type corresponding to the address
                (constants.FLOAT32, constants.INT32, etc.).
            value: The value to write.

        Raises:
            LJMError: An error was returned from the LJM library call.

        """
        ljm.eWriteAddress(self.handle, address, dataType, value)
        
    
    def eReadAddress(self, address, dataType):
        """Performs Modbus operations that reads a value from a device.
    
        Args:
            address: Register address to read.
            dataTypes: The data type corresponding to the address
                (constants.FLOAT32, constants.INT32, etc.).
    
        Returns:
            The read value.
    
        Raises:
            LJMError: An error was returned from the LJM library call.
    
        """
        return ljm.eReadAddress(self.handle, address, dataType)


    def eWriteName(self, name, value):
        """Performs Modbus operations that writes a value to a device.

        Args:
            name: Register name (string) to write.
            value: The value to write.
    
        Raises:
            TypeError: name is not a string.
            LJMError: An error was returned from the LJM library call.
    
        """
        ljm.eWriteName(self.handle, name, value)


    def eReadName(self, name):
        """Performs Modbus operations that reads a value from a device.
    
        Args:
            name: Register name (string) to read.
    
        Returns:
            The read value.
    
        Raises:
            TypeError: name is not a string.
            LJMError: An error was returned from the LJM library call.

        """
        return ljm.eReadName(self.handle, name)

    
    def eReadAddresses(self, numFrames, aAddresses, aDataTypes):
        """Performs Modbus operations that reads values from a device.

        Args:
            numFrames: The total number of reads to perform.  This needs to
                be the length of aAddresses/aDataTypes or less.
            aAddresses: List of register addresses to read.
            aDataTypes: List of data types corresponding to aAddresses
                (constants.FLOAT32, constants.INT32, etc.).

        Returns:
            A list of read values.

        Raises:
            LJMError: An error was returned from the LJM library call.

        """
        return ljm.eReadAddresses(self.handle, numFrames, aAddresses, aDataTypes)
    
    
    def eReadNames(self, numFrames, names):
        """Performs Modbus operations that reads values from a device.
    
        Args:
            numFrames: The total number of reads to perform.  This needs to
                be the length of names or less.
            names: List of register names (strings) to read.
    
        Returns:
            A list of read values.
    
        Raises:
            TypeError: names is not a list of strings.
            LJMError: An error was returned from the LJM library call.
    
        """
        return ljm.eReadNames(self.handle, numFrames, names)


    def eWriteAddresses(self, numFrames, aAddresses, aDataTypes, aValues):
        """Performs Modbus operations that writes values to a device.

        Args:
            numFrames: The total number of writes to perform.  This needs to
                be the length of aAddresses/aDataTypes/aValues or less.
            aAddresses: List of register addresses to write.
            aDataTypes: List of data types corresponding to aAddresses
                (constants.FLOAT32, constants.INT32, etc.).
            aValues: The list of values to write.

        Raises:
            LJMError: An error was returned from the LJM library call.

        """
        ljm.eWriteAddresses(self.handle, numFrames, aAddresses, aDataTypes, aValues)


    def eWriteNames(self, numFrames, names, aValues):
        """Performs Modbus operations that writes values to a device.
    
        Args:
            numFrames: The total number of writes to perform.  This needs to
                be the length of names/aValues or less.
            names: List of register names (strings) to write.
            aValues: List of values to write.
    
        Raises:
            TypeError: names is not a list of strings.
            LJMError: An error was returned from the LJM library call.
    
        """
        ljm.eWriteNames(self.handle, numFrames, names, aValues)


    def eAddresses(self, numFrames, aAddresses, aDataTypes, aWrites, aNumValues, aValues):
        """Performs Modbus operations that reads/writes values to a device.
    
        Args:
            numFrames: The total number of reads/writes to perform.  This
                needs to be the length of aAddresses/aDataTypes/aWrites/
                aNumValues or less.
            aAddresses: List of register addresses to write.
            aDataTypes: List of data types corresponding to aAddresses
                (constants.FLOAT32, constants.INT32, etc.).
            aWrites: List of directions (constants.READ or constants.WRITE)
                corresponding to aAddresses.
            aNumValues: List of the number of values to read/write,
                corresponding to aWrites and aAddresses.
            aValues: List of values to write.  Needs to be the length of the
                sum of the aNumValues list's values.  Values corresponding
                to writes are written.
    
        Returns:
            The list of aValues written/read.
    
        Raises:
            LJMError: An error was returned from the LJM library call.
    
        Notes:
            For every entry in aWrites[i] that is constants.WRITE, aValues
            contains aNumValues[i] values to write and for every entry in
            aWrites that is constants.READ, aValues contains aNumValues[i]
            values that will be updated in the returned list. aValues values
            must be in the same order as the rest of the lists. For example,
            if aWrite is:
                [constants.WRITE, constants.READ, constants.WRITE]
            and aNumValues is:
                [1, 4, 2]
            aValues would have one value to be written, then 4 blank/garbage
            values, and then 2 values to be written.
    
        """
        return ljm.eAddresses(self.handle, numFrames, aAddresses, aDataTypes, aWrites, aNumValues, aValues)
    
    
    def eNames(self, numFrames, names, aWrites, aNumValues, aValues):
        """Performs Modbus operations that reads/writes values to a device.
    
        Args:
            numFrames: The total number of reads/writes to perform.  This
                needs to be the length of names/aWrites/aNumValues or less.
            names: List of register names (strings) to write/read.
            aWrites: List of directions (constants.READ or constants.WRITE)
                corresponding to names.
            aNumValues: List of the number of values to read/write,
                corresponding to aWrites and names.
            aValues: List of values to write.  Needs to be the length of the
                sum of the aNumValues list's values.  Values corresponding
                to writes are written.
    
        Returns:
            The list of aValues written/read.
    
        Raises:
            TypeError: names is not a list of strings.
            LJMError: An error was returned from the LJM library call.
    
        Notes:
            For every entry in aWrites[i] that is constants.WRITE, aValues
            contains aNumValues[i] values to write and for every entry in
            aWrites that is constants.READ, aValues contains aNumValues[i]
            values that will be updated in the returned list. aValues values
            must be in the same order as the rest of the lists. For example,
            if aWrite is:
                [constants.WRITE, constants.READ, constants.WRITE]
            and aNumValues is:
                [1, 4, 2]
            aValues would have one value to be written, then 4 blank/garbage
            values, and then 2 values to be written.
    
        """
        return ljm.eNames(self.handle, numFrames, names, aWrites, aNumValues, aValues)


    def eStreamStart(self, scansPerRead, numChannels, aScanList_Pos, aScanList_Neg, scanRate):
        """Initializes a stream object and begins streaming. This includes
           creating a buffer in LJM that collects data from the device.

        Args:
            scansPerRead: Number of scans returned by each call to the
                eStreamRead function as well as the number of scans
                buffered in LJM each time the device gives data to LJM.
            numChannels: The size of aScanList_Pos and aScanList_Neg.
            aScanList_Pos: List of Modbus addresses to collect samples
                from.
            aScanList_Neg: List of Modbus addresses corresponding to
                aScanList_Pos. Use GND (address 199 or constants.GND) for
                single-ended conversion, or specify addresses for
                differential conversion.
            scanRate: Sets the desired number of scans per second.
    
        Returns:
            The actual scan rate the device will scan at.
    
        Raises:
            LJMError: An error was returned from the LJM library call.
    
        Note: Channel configuration such as range and resolution must be
            handled elsewhere
    
        """
        return ljm.eStreamStart(self.handle, scansPerRead, numChannels, aScanList_Pos, aScanList_Neg, scanRate)


    def eStreamRead(self):
        """Returns data from an initialized and running LJM stream buffer.
        Waits for data to become available, if necessary.
    
        Returns:
            A tuple containing:
            (aData, numSkippedScans, deviceScanBacklog, ljmScanBackLog)
    
            aData: Stream data list with all channels interleaved. It will
                contain scansPerRead*numChannels values configured from
                eStreamStart. The data returned is removed from the LJM
                stream buffer.
            numSkippedScans: The number of scans for which the device
                buffer was too full to record new results. (Rounds up if
                relevant). Corresponding aData values are set to
                constants.DUMMY_VALUE.
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
        return ljm.eStreamRead(self.handle)
    
    def eStreamStop(self):
        """Stops the LJM library from streaming any more data from the
        device, while leaving any collected data in the LJM library's
        buffer to be read.
    
        Raises:
            LJMError: An error was returned from the LJM library call.
    
        """
        ljm.eStreamStop(self.handle)
    
    
    def eReadString(self, name):
        """Reads a string from a device.
    
        Args:
            name: The string name of a register to read.
    
        Returns:
            The read string.
    
        Raises:
            TypeError: name is not a string.
            LJMError: An error was returned from the LJM library call.
    
        Note: This is a convenience function for eNames.
    
        """
        return ljm.eReadString(self.handle, name)
    
    
    def eWriteString(self, name, string):
        """Writes a string to a device.
    
        Args:
            name: The string name of a register to write.
    
        Raises:
            TypeError: name is not a string.
            LJMError: An error was returned from the LJM library call.
    
        Note: This is a convenience function for eNames.
    
        """
        ljm.eWriteString(self.handle, name, string)
