"""
Demonstrates thermocouple configuration and  measurement using our LJTick-InAmp
(commonly used with the T4)

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
"""
from labjack import ljm
import sys

if __name__ == "__main__":
    # Open first found LabJack
    handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
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
    # That would be INA of an InAmp connected to the VS/GND/AIN0/AIN1 terminals
    channelName = "AIN0"
    # Gain setting on the InAmp
    gain = 51
    # Offset setting (V) on the InAmp
    offset = 1.25
    tcType = ljm.constants.ttK # Type K thermocouple
    # thermocoupleType = ljm.constants.ttB # Type B thermocouple
    # thermocoupleType = ljm.constants.ttE # Type E thermocouple
    # thermocoupleType = ljm.constants.ttJ # Type J thermocouple
    # thermocoupleType = ljm.constants.ttN # Type N thermocouple
    # thermocoupleType = ljm.constants.ttR # Type R thermocouple
    # thermocoupleType = ljm.constants.ttS # Type S thermocouple
    # thermocoupleType = ljm.constants.ttT # Type T thermocouple
    # thermocoupleType = ljm.constants.ttC # Type C thermocouple

    # Set the resolution index to the default setting
    # Default setting has different meanings depending on the device.
    # See our AIN documentation (linked above) for more information
    resIndexRegister = "%s_RESOLUTION_INDEX" % channelName
    ljm.eWriteName(handle, resIndexRegister, 0)

    # This section is for range and negative channel settings. The T4 does not
    # support these configurations
    if deviceType == ljm.constants.dtT7:
        # ±10 V range setting
        rangeRegister = "%s_RANGE" % channelName
        ljm.eWriteName(handle, rangeRegister, 10)
        # Set up a single ended measurement
        negChannelValue = ljm.constants.GND
        negChannelRegister = "%s_NEGATIVE_CH" % channelName
        ljm.eWriteName(handle, negChannelRegister, negChannelValue)
    elif deviceType == ljm.constants.dtT8:
        print("\nThe T8 is not compatible with the InAmp, see our AIN_EF example")
        exit(0)

    print("\nReading thermocouple temperature %d times...\n" % numIterations)
    i = 0
    intervalHandle = 1
    # Delay between readings (in microseconds)
    ljm.startInterval(intervalHandle, 1000000)

    while i < numIterations:
        try:
            # Read the InAmp output voltage and internal temp sensor at once
            aNames = [channelName, "TEMPERATURE_DEVICE_K"]
            [voltage, cjTempK] = ljm.eReadNames(handle, len(aNames), aNames)
            # Convert the InAmp output to the raw thermocouple voltage
            tcVolts = (voltage - offset) / gain
            # Convert voltage to thermocouple temperature (K).
            tcTempK = ljm.tcVoltsToTemp(tcType, tcVolts, cjTempK)
            # Print the temperature read
            print("%0.3f degrees Kelvin\n" % tcTempK)
            i = i + 1
            ljm.waitForNextInterval(intervalHandle)
        except Exception:
            print(sys.exc_info()[1])
            break

    # Close handles
    ljm.cleanInterval(intervalHandle)
    ljm.close(handle)
    print("Done!")