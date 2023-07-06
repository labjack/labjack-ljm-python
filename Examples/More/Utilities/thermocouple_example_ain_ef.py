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

    # Read 10 times
    numIterations = 10
    # Take a measurement of a thermocouple connected to AIN0
    channelName = "AIN0"
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
    tcIndex = 22
    # Temperature reading units (0=K, 1=C, 2=F)
    tempUnitIndex = 0

    # The CJC configurations should be set up such that:
    # tempK = reading * cjcSlope + cjcOffset
    # Where 'tempK' is the CJC reading in Kelvin and 'reading' is the value
    # read from the register at cjcAddress.
    # Use TEMPERATURE_DEVICE_K for CJC
    cjcAddress = 60052
    # CJC slope when using TEMPERATURE_DEVICE_K
    cjcSlope = 1.0
    # CJC offset when using TEMPERATURE_DEVICE_K
    cjcOffset = 0.0


    # Set the resolution index to the default setting
    # Default setting has different meanings depending on the device.
    # See our AIN documentation (linked above) for more information
    resIndexRegister = "%s_RESOLUTION_INDEX" % channelName
    ljm.eWriteName(handle, resIndexRegister, 0)

    # Set up any negative channel configurations required. The T8 inputs are
    # isolated and therefore do not require any negative channel configuration
    if deviceType == ljm.constants.dtT7:
        # There are only certain valid differential channel pairs. For AIN0-13
        # the valid pairs are an even numbered AIN and next odd AIN. For
        # example, AIN0-AIN1, AIN2-AIN3. To take a differential reading between
        # AIN0 and AIN1, set AIN0_NEGATIVE_CH to 1

        # Set up a single ended measurement
        negChannelValue = ljm.constants.GND
        negChannelRegister = "%s_NEGATIVE_CH" % channelName
        ljm.eWriteName(handle, negChannelRegister, negChannelValue)
    elif deviceType == ljm.constants.dtT4:
        print("\nThe T4 does not support the thermocouple AIN_EF, see our InAmp thermocouple example")
        exit(0)

    # Configure all of the necessary thermocouple AIN_EF registers
    aNames = []
    aValues = []
    # For setting up the AIN#_EF_INDEX (thermocouple type)
    indexRegister = "%s_EF_INDEX" % channelName
    aNames.append(indexRegister)
    aValues.append(tcIndex)
    # For setting up the AIN#_EF_CONFIG_A (temperature units)
    configA = "%s_EF_CONFIG_A" % channelName
    aNames.append(configA)
    aValues.append(tempUnitIndex)
    # For setting up the AIN#_EF_CONFIG_B (CJC address)
    configB = "%s_EF_CONFIG_B" % channelName
    aNames.append(configB)
    aValues.append(cjcAddress)
    # For setting up the AIN#_EF_CONFIG_D (CJC slope)
    configD = "%s_EF_CONFIG_D" % channelName
    aNames.append(configD)
    aValues.append(cjcSlope)
    # For setting up the AIN#_EF_CONFIG_E (CJC offset)
    configE = "%s_EF_CONFIG_E" % channelName
    aNames.append(configE)
    aValues.append(cjcOffset)
    # Write all of the AIN_EF settings
    ljm.eWriteNames(handle, len(aNames), aNames, aValues)

    print("\nReading thermocouple temperature %d times...\n" % numIterations)
    i = 0
    intervalHandle = 1
    # AIN#_EF_READ_A returns the thermocouple temperature reading
    readA = "%s_EF_READ_A" % channelName
    # Delay between readings (in microseconds)
    ljm.startInterval(intervalHandle, 1000000)

    while i < numIterations:
        try:
            # Read the thermocouple temperature
            tcTemp = ljm.eReadName(handle, readA)
            # Print the temperature read
            print("%0.3f degrees\n" % tcTemp)
            i = i + 1
            ljm.waitForNextInterval(intervalHandle)
        except Exception:
            print(sys.exc_info()[1])
            break

    # Close handles
    ljm.cleanInterval(intervalHandle)
    ljm.close(handle)
    print("Done!")