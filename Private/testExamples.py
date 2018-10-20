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
print("------------")
os.chdir("../../Basic")
exec(open("eWriteName.py").read())
print("------------")
exec(open("eReadName.py").read())
print("------------")
exec(open("eWriteNames.py").read())
print("------------")
exec(open("eReadNames.py").read())
print("------------")
exec(open("eNames.py").read())
print("------------")

exec(open("eWriteAddress.py").read())
print("------------")
exec(open("eReadAddress.py").read())
print("------------")
exec(open("eWriteAddresses.py").read())
print("------------")
exec(open("eReadAddresses.py").read())
print("------------")
exec(open("eAddresses.py").read())
print("------------")
sys.argv = ["write_read_loop_with_config.py", "5"]
exec(open("write_read_loop_with_config.py").read())
print("------------")

# Skipping 1-Wire test. Needs connections for testing.

os.chdir("../More/AIN")
exec(open("single_ain.py").read())
print("------------")
exec(open("single_ain_with_config.py").read())
print("------------")
sys.argv = ["dual_ain_loop.py", "5"]
exec(open("dual_ain_loop.py").read())
print("------------")
sys.argv = []

os.chdir("../Config")
if TEST_WRITES:
    exec(open("write_device_name_string.py").read())
    print("------------")
    exec(open("write_power_config.py").read())
    print("------------")
exec(open("read_config.py").read())
print("------------")
exec(open("read_device_name_string.py").read())
print("------------")

os.chdir("../DIO")
exec(open("single_dio_read.py").read())
print("------------")
exec(open("single_dio_write.py").read())
print("------------")

os.chdir("../DIO_EF")
exec(open("dio_ef_config_1_pwm_and_1_counter.py").read())
print("------------")

os.chdir("../Ethernet")
if TEST_WRITES:
    exec(open("write_ethernet_config.py").read())
    print("------------")
exec(open("read_ethernet_config.py").read())
print("------------")
exec(open("read_ethernet_mac.py").read())
print("------------")

os.chdir("../I2C")
exec(open("i2c_eeprom.py").read())
print("------------")

os.chdir("../SPI")
exec(open("spi.py").read())
print("------------")

os.chdir("../Stream")
sys.path.append(".")
exec(open("stream_basic.py").read())
print("------------")
exec(open("stream_basic_with_stream_out.py").read())
print("------------")
exec(open("stream_burst.py").read())
print("------------")
exec(open("stream_sequential_ain.py").read())
print("------------")
exec(open("stream_callback.py").read())
print("------------")
#exec(open("stream_triggered.py").read())
#print("------------")
exec(open("in_stream_with_non_looping_out_stream.py").read())
print("------------")

os.chdir("../Testing")
exec(open("c-r_speed_test.py").read())
print("------------")

os.chdir("../Watchdog")
if TEST_WRITES:
    exec(open("write_watchdog_config.py").read())
    print("------------")
exec(open("read_watchdog_config.py").read())

os.chdir("../WiFi")
if TEST_WRITES:
    try:
        print("------------")
        exec(open("write_wifi_config.py").read())
    except SystemExit:
        pass
try:
    print("------------")
    exec(open("read_wifi_config.py").read())
except SystemExit:
    pass
try:
    print("------------")
    exec(open("read_wifi_rssi.py").read())
except SystemExit:
    pass
try:
    print("------------")
    exec(open("read_wifi_mac.py").read())
except SystemExit:
    pass

print("------------")
print("\n+++ Test Success +++")
