"""
Demonstrates using the BMP180 temperature and humidity sensor connected on the
LabJack I2C bus.

This requires the associated example Lua script temp-and-pressure-BMP180.lua,
which needs to be running on the LabJack device. In the Kipling application,
this script can be loaded under
Examples > I2C > Temperature & Pressure BMP180, and can be configured to run at
device start up.

***See Lua script for electrical connections.***

Data is transfered using the USER_RAM registers, which are written from the Lua
script and read from the Python script.

The calculations are taken directly from the BMP180 datasheet, which can
be found at:

https://media.digikey.com/pdf/Data%20Sheets/Bosch/BMP180.pdf

"""

import math
import sys
import time

from labjack import ljm


# Open first found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
#handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
#handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
#handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per mb: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Ensure that a lua script is running on the T7. If not, end the python script.
if(ljm.eReadName(handle, "LUA_RUN") != 1):
    print("There is no Lua script running on the device.")
    print("Please use Kipling to begin a Lua script on the device.")
    sys.exit()

# Load the calibration constants for the BMP180 from USER_RAM Registers.
calAddrNames = ["USER_RAM11_F32", "USER_RAM12_F32", "USER_RAM13_F32",
                "USER_RAM14_F32", "USER_RAM15_F32", "USER_RAM16_F32",
                "USER_RAM17_F32", "USER_RAM18_F32", "USER_RAM19_F32",
                "USER_RAM20_F32", "USER_RAM21_F32"
                ]

calConst = ljm.eReadNames(handle, 11, calAddrNames)
ac1 = calConst[0] 
ac2 = calConst[1]
ac3 = calConst[2]
ac4 = calConst[3]
ac5 = calConst[4]
ac6 = calConst[5]
b1  = calConst[6]
b2  = calConst[7]
mb  = calConst[8]
mc  = calConst[9]
md  = calConst[10]

while True:
    try:
        ut = ljm.eReadName(handle, "USER_RAM9_F32")
        up = ljm.eReadName(handle, "USER_RAM10_F32")   

        # BMP180 datasheet calculations
        x1 = (ut-ac6) * ac5 / 2**15
        x2 = mc * (2**11) / (x1 + md)
        b5 = x1 + x2
        tempC = ((b5+8)/2**4) / 10
        tempF = (tempC*(9.0/5)) + 32

        b6 = b5 - 400
        x1 = (b2*(b6*b6/(2*12))) / 2**11
        x2 = ac2 * b6 / 2**11
        x3 = x1 + x2
        b3 = ((ac1*4+x3)+2) / 4
        x1 = ac3*b6 / 2**13
        x2 = (b1*(b6*b6/2**12)) / 2**16
        x3 = ((x1+x2) + 2) / 4
        b4 = ac4 * (x3+32768) / 2**15
        b7 = (up-b3) * 50000
        if b7 < 0x80000000:
            pressureRaw = (b7*2) / b4
        else:
            pressureRaw = (b7/b4) * 2
        x1 = (pressureRaw/2**8) * (pressureRaw/2**8)
        x1 = (x1*3038) / 2**16
        x2 = (-7357*pressureRaw) / 2**16
        pressurePa = pressureRaw + (x1+x2+3791) / 2**4  # Pressure in Pascals
        pressureAtm =  (9.86923E-06) * pressurePa  # Pressure in Atmospheres

        print("Temp: %4.2fF (%4.2fC)     Pressure: %4.3f Atm (%04.2f KPa)" \
              %(tempF, tempC, pressureAtm, pressurePa/1000))
        time.sleep(1.00)  # Delay for 1 second between readings
    except KeyboardInterrupt:
        # Exit the loop upon Ctrl+C to allow closing the LabJack properly
        break

print("Closing LabJack")
ljm.close(handle)
