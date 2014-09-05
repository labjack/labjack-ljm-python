"""
Runs all examples. If an exception stops the program, fix it.
Examples that change startup configurations are disabled by default and need
to be turned on with TEST_WRITES.

"""

TEST_WRITES = False

dir = "../Examples/"

#execfile(dir + "")
execfile(dir + "eWriteName.py")
execfile(dir + "eReadName.py")
execfile(dir + "eWriteNames.py")
execfile(dir + "eReadNames.py")
execfile(dir + "eNames.py")

execfile(dir + "eWriteAddress.py")
execfile(dir + "eReadAddress.py")
execfile(dir + "eWriteAddresses.py")
execfile(dir + "eReadAddresses.py")
execfile(dir + "eAddresses.py")

execfile(dir + "/AIN/single_ain.py")
execfile(dir + "/AIN/single_ain_with_config.py")

if TEST_WRITES:
    execfile(dir + "/Config/write_device_name_string.py")
    execfile(dir + "/Config/write_power_config.py")
execfile(dir + "/Config/read_config.py")
execfile(dir + "/Config/read_device_name_string.py")

execfile(dir + "/DIO/single_dio_read.py")
execfile(dir + "/DIO/single_dio_write.py")

execfile(dir + "/DIO_EF/dio_ef_config_1_pwm_and_1_counter.py")

execfile(dir + "/Ethernet/read_ethernet_config.py")
execfile(dir + "/Ethernet/read_ethernet_mac.py")
execfile(dir + "/Ethernet/write_ethernet_config.py")

execfile(dir + "/I2C/i2c_eeprom.py")

execfile(dir + "/SPI/spi.py")

execfile(dir + "/Stream/stream_basic.py")
execfile(dir + "/Stream/o_stream_run.py")

execfile(dir + "/Testing/c-r_speed_test.py")

if TEST_WRITES:
    execfile(dir + "/Watchdog/write_watchdog_config.py")
execfile(dir + "/Watchdog/read_watchdog_config.py")

if TEST_WRITES:
    execfile(dir + "/WiFi/write_wifi_config.py")

execfile(dir + "/WiFi/read_wifi_config.py")
execfile(dir + "/WiFi/read_wifi_rssi.py")
execfile(dir + "/WiFi/read_wifi_mac.py")

execfile(dir + "/AIN/dual_ain_loop.py") #Requires ctrl-C, so run last
