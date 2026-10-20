"""
Demonstrates thermocouple configuration and measurement using the thermocouple
AIN_EF (T7/T8 only).

Relevant Documentation:

Thermocouple App-Note:
    https://labjack.com/support/app-notes/thermocouples

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    Single Value Functions (such as eWriteName and eReadName):
        https://labjack.com/support/software/api/ljm/function-reference/single-value-functions
    Multiple Value Functions (such as eReadNames):
        https://labjack.com/support/software/api/ljm/function-reference/multiple-value-functions
    Timing Functions (such as StartInterval, WaitForNextInterval and
    CleanInterval):
        https://labjack.com/support/software/api/ljm/function-reference/timing-functions

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Analog Inputs:
        https://labjack.com/support/datasheets/t-series/ain
    Thermocouple AIN_EF (T7/T8 only):
        https://labjack.com/support/datasheets/t-series/ain/extended-features/thermocouple
"""
import sys

from labjack import ljm

class ThermocoupleAINEF:
    """Class for thermocouple AIN_EF operations.

        Attributes:
            tcIndex: AIN#_EF_INDEX corresponding to a thermocouple type.
            ainChannel: AIN register name to get thermocouple readings from.
            cjcName: Register name to get CJC readings from.
            cjcAddress: Register address to get CJC readings. Automatically
            interpreted from cjcName.
            cjcSlope: Slope of CJC register to Kelvin conversion.
            cjcOffset: Offset for CJC temp (in Kelvin).
            tempUnitIndex: Index that determines the output temp units.
            0=K, 1=C, 2=F.
            tempUnit: String representation of the output temp units.
            Automatically interpreted from tempUnitIndex.
    """
    def __init__(
        self,
        tcIndex,
        ainChannel,
        cjcName,
        cjcSlope,
        cjcOffset,
        tempUnitIndex
    ):
        self.tcIndex = tcIndex
        self.ainChannel = ainChannel
        self.cjcName = cjcName
        self.cjcAddress = ljm.nameToAddress(self.cjcName)[0]
        self.cjcSlope = cjcSlope
        self.cjcOffset = cjcOffset
        self.tempUnitIndex = tempUnitIndex
        self.tempUnit = {0: "K", 1: "C", 2: "F"}[self.tempUnitIndex]

    def setup(self, handle):
        """Configures all of the necessary thermocouple AIN_EF registers

        Args:
            handle: LJM device connection handle.
        Returns:
            None.
        Raises:
            LJMError: An error was returned from the eWriteNames call.
        """
        aNames = []
        aValues = []

        # For setting up the AIN#_EF_INDEX (thermocouple type)
        indexRegister = "%s_EF_INDEX" % self.ainChannel
        aNames.append(indexRegister)
        aValues.append(self.tcIndex)

        # For setting up the AIN#_EF_CONFIG_A (temperature units)
        configA = "%s_EF_CONFIG_A" % self.ainChannel
        aNames.append(configA)
        aValues.append(self.tempUnitIndex)

        # For setting up the AIN#_EF_CONFIG_B (CJC address)
        configB = "%s_EF_CONFIG_B" % self.ainChannel
        aNames.append(configB)
        aValues.append(self.cjcAddress)

        # For setting up the AIN#_EF_CONFIG_D (CJC slope)
        configD = "%s_EF_CONFIG_D" % self.ainChannel
        aNames.append(configD)
        aValues.append(self.cjcSlope)

        # For setting up the AIN#_EF_CONFIG_E (CJC offset)
        configE = "%s_EF_CONFIG_E" % self.ainChannel
        aNames.append(configE)
        aValues.append(self.cjcOffset)

        # Write all of the AIN_EF settings
        ljm.eWriteNames(handle, len(aNames), aNames, aValues)

    def getReadings(self, handle):
        """Reads the thermocouple AIN_EF tcTemp, tcVolts, and CJtemp.

        Args:
            handle: LJM device connection handle.
        Returns:
            A list containing tcTemp, tcVolts, and cjTemp in that order.
        Raises:
            LJMError: An error was returned from the eReadNames call.
        """
        # AIN#_EF_READ_A returns the thermocouple temperature reading
        readA = "%s_EF_READ_A" % self.ainChannel

        # AIN#_EF_READ_B returns the thermocouple voltage reading
        readB = "%s_EF_READ_B" % self.ainChannel

        # AIN#_EF_READ_C returns the thermocouple CJC temperature reading
        readC = "%s_EF_READ_C" % self.ainChannel
        return ljm.eReadNames(handle, 3, [readA, readB, readC])

    def getTempUnit(self):
        """ Returns AIN_EF output temperature units as a string.

        Args:
            None
        Returns:
            A string (character) of the AIN_EF output temperature units.
        """
        return self.tempUnit


if __name__ == "__main__":
    # Open first found LabJack
    handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
    #handle = ljm.openS("T8", "ANY", "ANY")  # T8 device, Any connection, Any identifier
    #handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
    #handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

    info = ljm.getHandleInfo(handle)
    print("Opened a LabJack with Device type: %i," % info[0] +
        " Connection type: %i,\n" % info[1] +
        "Serial number: %i," % info[2] +
        " IP address: %s," % ljm.numberToIP(info[3]) +
        " Port: %i,\n" % info[4] +
        "Max bytes per MB: %i" % info[5]
    )
    deviceType = info[0]

    # Read 10 times
    numIterations = 10

    # Take a measurement of a thermocouple connected to AIN0
    channel = 0
    channelName = "AIN%i" % channel

    # Thermocouple AIN_EF indices:
    # 20=type E
    # 21=type J
    # 22=type K
    # 23=type R
    # 24=type T
    # 25=type S
    # 27=type N
    # 28=type B
    # 30=type C
    tcIndex = 22 # Type K

    # The CJC configurations should be set up such that:
    # tempK = reading * cjcSlope + cjcOffset
    # Where 'tempK' is the CJC reading in Kelvin and 'reading' is the value
    # read from the register at cjcAddress.
    if deviceType == ljm.constants.dtT8:
        # Use TEMPERATURE# for T8 CJC. Since the thermocouple is
        # connected to AIN0, we are using TEMPERATURE0 for the CJC.
        cjcName = "TEMPERATURE%i" % channel
    else:
        # Use TEMPERATURE_DEVICE_K for CJC
        cjcName = "TEMPERATURE_DEVICE_K"

    cjcSlope = 1.0 # Use 55.56 for LM34.
    cjcOffset = 0.0 # Use 255.37 for LM34.
    tempUnitIndex = 0 # Temperature reading units (0=K, 1=C, 2=F)

    # Set up the AIN_EF
    ain0ef = ThermocoupleAINEF(
        tcIndex,
        channelName,
        cjcName,
        cjcSlope,
        cjcOffset,
        tempUnitIndex
    )
    ain0ef.setup(handle)

    # Set up some of the AIN registers
    aNames = []
    aValues = []
    # If you set range according to the max TC voltage amplitude,
    # the device will use the best/closest setting available.
    aNames.append("%s_RANGE" % channelName)
    aValues.append(0.07) # Will use ±0.1V on T7, ±0.075V on T8.
    aNames.append("%s_RESOLUTION_INDEX" % channelName)
    aValues.append(0) # Use the default resolution setting.

    # Set up any negative channel configurations required. The T8 inputs are
    # isolated and therefore do not require any negative channel configuration.
    if deviceType == ljm.constants.dtT7:
        # There are only certain valid differential channel pairs. For AIN0-13
        # the valid pairs are an even numbered AIN and next odd AIN. For
        # example, AIN0-AIN1, AIN2-AIN3. To take a differential reading between
        # AIN0 and AIN1, set AIN0_NEGATIVE_CH to 1.

        # Set up a single ended measurement (add the negative channel register
        # to the list of AIN registers to write).
        aNames.append("%s_NEGATIVE_CH" % channelName)
        aValues.append(ljm.constants.GND)
    elif deviceType == ljm.constants.dtT4:
        print(
            "\nThe T4 does not support the thermocouple AIN_EF." +
            " See our InAmp thermocouple example."
        )
        exit(0)
    # Write the AIN registers to the device
    ljm.eWriteNames(handle, len(aNames), aNames, aValues)

    print("\nReading thermocouple temperature %d times...\n" % numIterations)
    intervalHandle = 1
    # Delay between readings (in microseconds)
    ljm.startInterval(intervalHandle, 1000000)
    for i in range(numIterations):
        try:
            [tcTemp, tcVolts, cjTemp] = ain0ef.getReadings(handle)
            print(
                "TCTemp = %0.3f %s," % (tcTemp, ain0ef.getTempUnit()) +
                " TCVolts = %0.6f V," % tcVolts +
                " CJTemp = %0.3f %s\n" % (cjTemp, ain0ef.getTempUnit())
            )
            ljm.waitForNextInterval(intervalHandle)
        except Exception:
            print(sys.exc_info()[1])
            break

    # Close handles
    ljm.cleanInterval(intervalHandle)
    ljm.close(handle)
    print("Done!")
