from labjack.ljm.device import Device

class T7(Device):
    def __init__(self, connectionType="LJM_ctANY", identifier="LJM_idANY"):
        dt = 7
        if(isinstance(connectionType, str)):
            dt = "LJM_dtT7"
        Device.__init__(self, dt, connectionType, identifier)


    def openS(self, connectionType="LJM_ctANY", identifier="LJM_idANY"):
        """Opens a T7, and saves the handle.

        Args:
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
        self._openS(self, "LJM_dtT7", connectionType, identifier)


    def open(self, connectionType=0, identifier="LJM_idANY"):
        """Opens a T7, and saves the handle.

        Args:
            connectionType: An integer containing the type of connection
                desired (constants.ctUSB, constants.ctTCP, constants.ctANY,
                etc.).
            Identifier: A string identifying the device to connect to or
                "LJM_idANY". This can be a serial number, IP address, or
                device name. Device names may not contain periods.

        Raises:
            TypeError: connectionType is not an integer.
            LJMError: An error was returned from the LJM library call.

        Notes:
            Args are not case-sensitive.
            Empty strings indicate the same thing as "LJM_xxANY".
    
        """
        self._open(self, 7, connectionType, identifier)
