"""
Demonstrates thermocouple configuration and  measurement.
This example demonstrates usage of the thermocouple AIN_EF (T7/T8 only) and a
solution using our LJTick-InAmp (commonly used with the T4)

Relevant Documentation:

Thermocouple App-Note:
    https://labjack.com/support/app-notes/thermocouples

LJM Library:
    LJM Library Installer:
        https:#labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https:#labjack.com/support/software/api/ljm
    Opening and Closing:
        https:#labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    Single Value Functions(such as eReadName):
        https:#labjack.com/support/software/api/ljm/function-reference/single-value-functions
    TCVoltsToTemp:
        https:#labjack.com/support/software/api/ud/function-reference/tcvoltstotemp

T-Series and I/O:
    Modbus Map:
        https:#labjack.com/support/software/api/modbus/modbus-map
    Analog Inputs:
        https:#labjack.com/support/datasheets/t-series/ain
    Thermocouple AIN_EF (T7/T8 only):
        https://labjack.com/support/datasheets/t-series/ain/extended-features/thermocouple
"""
from labjack import ljm
import sys


class TCData:
    def __init__(self,
        tcType=ljm.constants.ttK,
        channel=0,
        CJCAddress=60052,
        CJCSlope=1,
        CJCOffset=0,
        tempUnits="C"):
        # Supported TC types are:
        #     ljm.constants.ttB (val=6001)
        #     ljm.constants.ttE (val=6002)
        #     ljm.constants.ttJ (val=6003)
        #     ljm.constants.ttK (val=6004)
        #     ljm.constants.ttN (val=6005)
        #     ljm.constants.ttR (val=6006)
        #     ljm.constants.ttS (val=6007)
        #     ljm.constants.ttT (val=6008)
        #     ljm.constants.ttC (val=6009)
        # Note that the values above do not align with the AIN_EF index values
        # or order. In this example, we demonstrate a lookup table to convert
        # our thermocouple constant to the correct index when using the AIN_EF
        self.__tcType = tcType

        self.__channel = channel

        # Modbus address to read the CJC sensor at.
        self.__CJCAddress = CJCAddress

        # Slope of CJC voltage to Kelvin conversion (K/volt). TEMPERATURE_DEVICE_K
        # returns temp in K, so this would be set to 1 if using it for CJC. If
        # using an LM34 on some AIN for CJC, this config should be 55.56
        self.__CJCSlope = CJCSlope

        # Offset for CJC temp (in Kelvin).This would normally be 0 if reading the
        # register TEMPERATURE_DEVICE_K for CJC. If using an InAmp or expansion
        # board, the CJ might be a bit cooler than the internal temp sensor, so
        # you might adjust the offset down a few degrees. If using an LM34 on some
        # AIN for CJC, this config should be 255.37
        self.__CJCOffset = CJCOffset

        if (tempUnits != "K" and tempUnits != "C" and tempUnits != "F"):
            raise Exception("Invalid tempUnits passed to TCData constructor")
        self.__tempUnits = tempUnits

    def SetupAIN_EF(self, handle):
        try:
            # For converting LJM TC type constant to TC AIN_EF index
            # Thermocouple type:
            #                B  E  J  K  N  R  S  T  C
            TC_INDEX_LUT = [28,20,21,22,27,23,25,24,30]
            # map the designated temp unit to config values
            tempUnitConfigVal = {"K":0, "C":1, "F":2}
            aAddresses = []
            aTypes = []
            aValues = []

            # For setting up the AIN#_EF_INDEX (thermocouple type)
            aAddresses.append(9000+2*self.__channel)
            aTypes.append(ljm.constants.UINT32)
            aValues.append(TC_INDEX_LUT[self.__tcType - 6001])

            # For setting up the AIN#_EF_CONFIG_A (temperature units)
            aAddresses.append(9300+2*self.__channel)
            aTypes.append(ljm.constants.UINT32)
            aValues.append(tempUnitConfigVal[self.__tempUnits])

            # For setting up the AIN#_EF_CONFIG_B (CJC address)
            aAddresses.append(9600+2*self.__channel)
            aTypes.append(ljm.constants.UINT32)
            aValues.append(self.__CJCAddress)

            # For setting up the AIN#_EF_CONFIG_D (CJC slope)
            aAddresses.append(10200+2*self.__channel)
            aTypes.append(ljm.constants.FLOAT32)
            aValues.append(self.__CJCSlope)

            # For setting up the AIN#_EF_CONFIG_E (CJC offset)
            aAddresses.append(10500+2*self.__channel)
            aTypes.append(ljm.constants.FLOAT32)
            aValues.append(self.__CJCOffset)

            ljm.eWriteAddresses(handle, len(aAddresses), aAddresses, aTypes, aValues)
        except ljm.LJMError as e:
            raise ljm.LJMError(errorString="Exception in TCData.SetupAIN_EF: " + str(e))

    def GetReadingsInAmp(self, handle, inAmpOffset=0.4, inAmpGain=51):
        try:
            # Read the thermocouple connected AIN
            TCVolts = ljm.eReadAddress(handle, 2*self.__channel, ljm.constants.FLOAT32)

            # Account for LJTick-InAmp scaling
            TCVolts = (TCVolts - inAmpOffset) / inAmpGain

            CJTemp = ljm.eReadAddress(handle, self.__CJCAddress, ljm.constants.FLOAT32)

            # Apply scaling to CJC reading if necessary
            # At this point, the reading must be in units Kelvin
            CJTemp = CJTemp * tcData.__CJCSlope + tcData.__CJCOffset;

            # Convert voltage reading to the thermocouple temperature (K).
            TCTemp = ljm.tcVoltsToTemp(self.__tcType, TCVolts, CJTemp)

            # Convert temp units for display if necessary
            if (self.__tempUnits == "C"):
                TCTemp = TCTemp-273.15
                CJTemp = CJTemp-273.15

            elif (self.__tempUnits == "F"):
                TCTemp = (1.8*TCTemp)-459.67
                CJTemp = (1.8*CJTemp)-459.67

            print("TCTemp: %lf %c,\t TCVolts: %lf,\tCJTemp: %lf %c\n" %
                (TCTemp, self.__tempUnits, TCVolts, CJTemp, self.__tempUnits))
        except ljm.LJMError as e:
            raise ljm.LJMError(errorString="Exception in TCData.GetReadingsInAmp: " + str(e))

    def GetReadingsAIN_EF(self, handle):
        try:
            TCVolts = ljm.eReadAddress(handle, 7300+2*self.__channel, ljm.constants.FLOAT32)
            CJTemp = ljm.eReadAddress(handle, 7600+2*self.__channel, ljm.constants.FLOAT32)
            TCTemp = ljm.eReadAddress(handle, 7000+2*self.__channel, ljm.constants.FLOAT32)

            print("TCTemp: %lf %c,\t TCVolts: %lf,\tCJTemp: %lf %c\n" %
                (TCTemp, self.__tempUnits, TCVolts, CJTemp, self.__tempUnits))
        except ljm.LJMError as e:
            raise ljm.LJMError(errorString="Exception in TCData.GetReadingsAIN_EF: " + str(e))


if __name__ == "__main__":
    # Open first found LabJack
    handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
    #handle = ljm.openS("T8", "ANY", "ANY")  # T8 device, Any connection, Any identifier
    #handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
    #handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
    #handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

    info = ljm.getHandleInfo(handle)
    print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
          "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
          (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))
    deviceType = info[0]

    channel = 0 # Read a thermocouple on AIN0
    # Initialize our thermocouple data class (defined above)
    tcData = TCData(tcType=ljm.constants.ttK,
        channel=channel,
        CJCAddress=60052,
        CJCSlope=1,
        CJCOffset=0,
        tempUnits="C")

    # Set the resolution index to the default setting
    # Default setting has different meanings depending on the device.
    # See our AIN documentation (linked above) for more information
    ljm.eWriteName(handle, "AIN_ALL_RESOLUTION_INDEX", 0)

    if deviceType != ljm.constants.dtT4:
        # Set up the AIN_EF if using a T7/T8
        tcData.SetupAIN_EF(handle)

        # Only set up the negative channel config if using a T7
        # Set up a single ended measurement (AIN#_NEGATIVE_CH = GND)
        # If taking a differential reading on a T7, channel should be an even
        # numbered AIN connecting signal+, and signal- should be connected to
        # the positive AIN channel plus one.
        # Example: signal+=channel=0 (AIN0), signal-=negChannel=1 (AIN1)
        if deviceType == ljm.constants.dtT7:
            negChannel = ljm.constants.GND
            ljm.eWriteAddress(handle, 41000+channel,
                ljm.constants.UINT16, negChannel)

    intervalHandle = 1
    # Delay between readings (in microseconds)
    ljm.startInterval(intervalHandle, 1000000)

    while True:
        try:
            if deviceType != ljm.constants.dtT4:
                tcData.GetReadingsAIN_EF(handle)
            else:
                tcData.GetReadingsInAmp(handle, inAmpOffset=0.4, inAmpGain=51)
            ljm.waitForNextInterval(intervalHandle)
        except KeyboardInterrupt:
            break
        except Exception:
            print(sys.exc_info()[1])
            break

    # Close handles
    ljm.cleanInterval(intervalHandle)
    ljm.close(handle)