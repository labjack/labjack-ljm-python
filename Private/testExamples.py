"""
Runs all examples. If an exception stops the program, fix it.
Examples that change startup configurations are disabled by default and need
to be turned on with TEST_WRITES.

"""
from labjack.ljm import LJMError
import sys
import os

TEST_WRITES = False

#os.chdir(directoryName)
#exec(open(fileName).read())

os.chdir("../Examples/")
os.chdir("More/List_All")

exec(open("list_all.py").read())

os.chdir("../../Basic")
exec(open("eWriteName.py").read())
exec(open("eReadName.py").read())
exec(open("eWriteNames.py").read())
exec(open("eReadNames.py").read())
exec(open("eNames.py").read())

exec(open("eWriteAddress.py").read())
exec(open("eReadAddress.py").read())
exec(open("eWriteAddresses.py").read())
exec(open("eReadAddresses.py").read())
exec(open("eAddresses.py").read())

os.chdir("../More/AIN")
exec(open("single_ain.py").read())
exec(open("single_ain_with_config.py").read())
sys.argv = ["dual_ain_loop.py", "5"]
exec(open("dual_ain_loop.py").read())
sys.argv = []

os.chdir("../Config")
if TEST_WRITES:
    exec(open("write_device_name_string.py").read())
    exec(open("write_power_config.py").read())
exec(open("read_config.py").read())
exec(open("read_device_name_string.py").read())

os.chdir("../DIO")
exec(open("single_dio_read.py").read())
exec(open("single_dio_write.py").read())

os.chdir("../DIO_EF")
exec(open("dio_ef_config_1_pwm_and_1_counter.py").read())

os.chdir("../Ethernet")
if TEST_WRITES:
    exec(open("write_ethernet_config.py").read())
exec(open("read_ethernet_config.py").read())
exec(open("read_ethernet_mac.py").read())

os.chdir("../I2C")
exec(open("i2c_eeprom.py").read())

os.chdir("../SPI")
exec(open("spi.py").read())

os.chdir("../Stream")
exec(open("stream_basic.py").read())
exec(open("stream_basic_with_stream_out.py").read())
exec(open("stream_sequential_ain.py").read())
sys.path.append(".")
exec(open("in_stream_with_non_looping_out_stream.py").read())

os.chdir("../Testing")
exec(open("c-r_speed_test.py").read())

os.chdir("../Watchdog")
if TEST_WRITES:
    exec(open("write_watchdog_config.py").read())
exec(open("read_watchdog_config.py").read())

os.chdir("../WiFi")
if TEST_WRITES:
    exec(open("write_wifi_config.py").read())
exec(open("read_wifi_config.py").read())
exec(open("read_wifi_rssi.py").read())
exec(open("read_wifi_mac.py").read())

print("\n+++ Test Success +++")
