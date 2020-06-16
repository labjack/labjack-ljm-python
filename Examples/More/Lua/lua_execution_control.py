"""
Demonstrates how to control lua script execution with an LJM host app

Relevant Documentation:
 
LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    Single Value Functions (like eReadName):
        https://labjack.com/support/software/api/ljm/function-reference/single-value-functions
    Multiple Value Functions(such as eReadNameByteArray):
        https://labjack.com/support/software/api/ljm/function-reference/multiple-value-functions
 
T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    User-RAM:
        https://labjack.com/support/datasheets/t-series/lua-scripting#user-ram

"""
from labjack import ljm
from time import sleep

def loadLuaScript(handle, luaScript):
    """Function that loads and begins running a lua script

    """
    try:
        scriptLen = len(luaScript)
        # LUA_RUN must be written to twice to disable any running scripts.
        print("Script length: %u\n" % scriptLen)
        ljm.eWriteName(handle, "LUA_RUN", 0)
        # Then, wait for the Lua VM to shut down. Some T7 firmware
        # versions need a longer time to shut down than others.
        sleep(0.6)
        ljm.eWriteName(handle, "LUA_RUN", 0)
        ljm.eWriteName(handle, "LUA_SOURCE_SIZE", scriptLen)
        ljm.eWriteNameByteArray(handle, "LUA_SOURCE_WRITE", scriptLen, luaScript)
        ljm.eWriteName(handle, "LUA_DEBUG_ENABLE", 1)
        ljm.eWriteName(handle, "LUA_DEBUG_ENABLE_DEFAULT", 1)
        ljm.eWriteName(handle, "LUA_RUN", 1)
    except ljm.LJMError: 
        print("Error while loading the lua script")
        raise

def readLuaInfo(handle):
    """Function that selects the current lua execution block and prints
       out associated info from lua

    """
    try:
        for i in range(20):
            # The script sets the interval length with LJ.IntervalConfig.
            # Note that LJ.IntervalConfig has some jitter and that this program's
            # interval (set by sleep) will have some minor drift from
            # LJ.IntervalConfig.
            sleep(1)
            print("LUA_RUN: %d" % ljm.eReadName(handle, "LUA_RUN"))
            # Add custom logic to control the Lua execution block
            executionLoopNum = i % 3
            # Write which lua control block to run using the user ram register
            ljm.eWriteName(handle, "USER_RAM0_U16", executionLoopNum)
            numBytes = ljm.eReadName(handle, "LUA_DEBUG_NUM_BYTES")
            if (int(numBytes) == 0):
                continue
            print("LUA_DEBUG_NUM_BYTES: %d\n" % numBytes)
            aBytes = ljm.eReadNameByteArray(handle, "LUA_DEBUG_DATA", int(numBytes))
            luaMessage = "".join([("%c" % val) for val in aBytes])
            print("LUA_DEBUG_DATA: %s" % luaMessage)
    except ljm.LJMError:
        print("Error while running the main loop")
        raise


def main():
    try:
        luaScript = """-- Use USER_RAM0_U16 (register 46180) to determine which control loop to run
                    local ramval = 0
                    MB.W(46180, 0, ramval)
                    local loop0 = 0
                    local loop1 = 1
                    local loop2 = 2

                    -- Setup an interval to control loop execution speed. Update every second
                    LJ.IntervalConfig(0,1000)
                    while true do
                      if LJ.CheckInterval(0) then
                        ramval = MB.R(46180, 0)

                        if ramval == loop0 then
                          print("using loop0")
                        end

                        if ramval == loop1 then
                          print("using loop1")
                        end

                        if ramval == loop2 then
                          print("using loop2")
                        end

                      end
                    end"""
        # Open first found LabJack
        handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
        #handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
        #handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
        #handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

        info = ljm.getHandleInfo(handle)
        print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
              "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
              (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

        loadLuaScript(handle, luaScript)
        print("LUA_RUN %d" % ljm.eReadName(handle, "LUA_RUN"))
        print("LUA_DEBUG_NUM_BYTES: %d" % ljm.eReadName(handle, "LUA_DEBUG_NUM_BYTES"))
        readLuaInfo(handle)
        # Close handle
        ljm.close(handle)
    except ljm.LJMError:
        ljm.eWriteName(handle, "LUA_RUN", 0)
        # Close handle
        ljm.close(handle)
        raise
    except Exception:
        ljm.eWriteName(handle, "LUA_RUN", 0)
        # Close handle
        ljm.close(handle)
        raise

if __name__ == "__main__":
    main()
