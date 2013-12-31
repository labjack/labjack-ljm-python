from labjack import ljm
import timeit
import functools
import sys

def timeoutTest(h):
    try:
        ljm.readRaw(h, 2)
    except ljm.LJMError:
        e = sys.exc_info()[1]
        pass # print(e)

print("\nreadLibraryConfigS LJM_VERSION: " + str(ljm.readLibraryConfigS(ljm.constants.LIBRARY_VERSION)))
print("")

print("\n--- Function tests ----------------------\n")

print("loadConstants")
ljm.loadConstants()

#ljm.loadConstants()
dev = ljm.constants.dtT7
devS = 'T7'
con = ljm.constants.ctUSB
conS = 'USB'

print("errorToString: " + ljm.errorToString(0))
print(type(ljm.errorToString(0))) #"")
print(ljm.listAll(dev, con))
print(ljm.listAllS(devS, conS))

print("open")
print("")
h = ljm.open(dev, con)
ljm.close(h)

print("openS")
print("")
h = ljm.openS(devS, conS)
hInfo = ljm.getHandleInfo(h)
print("getHandleInfo: " + str(hInfo))
print("")

addrs = [0, 4]
dtypes = [ljm.constants.FLOAT32, ljm.constants.FLOAT32]
writes = [ljm.constants.READ, ljm.constants.READ]
nVals = [2, 2]
vals = [0, 0, 0, 0]
mbfb = ljm.addressesToMBFB(hInfo[5], addrs, dtypes, writes, nVals, vals, 2)
nFrames = mbfb[0]
wLi = mbfb[1]
print("addressesToMBFB: " + str(mbfb) + str(len(mbfb[1])))
print("")
r = ljm.mbfbComm(h, 0, mbfb[1])
print("mbfbComm: " + str(r))
print("")

print("updateValues: " + str(ljm.updateValues(r, dtypes, writes, nVals, 2)))
print("")

if dev == ljm.constants.dtT7:
    wLi[1] = 55
    print("writeRaw: " + str(wLi) + str(ljm.writeRaw(h, wLi)))
    print("")
    print("readRaw: " + str(ljm.readRaw(h, 24))) #expect bad checksum response [0xB8, 0xB8]
    print("")
else:
    print("writeRaw:" + str(ljm.writeRaw(h, [3]*10)))
    print("")
    print("readRaw:" + str(ljm.readRaw(h, 2))) #expect bad checksum response [0xB8, 0xB8]
    print("")

addr1 = 1000 #dac0
val1 = 2.3
print("eWriteAddress (" + str(addr1) + " " + str(val1) + "): " + str(ljm.eWriteAddress(h, addr1, ljm.constants.FLOAT32, val1)))
print("")
print("eReadAddress: " + str(ljm.eReadAddress(h, 0, ljm.constants.FLOAT32)))
print("")

print("eReadAddresses: " + str(ljm.eReadAddresses(h, 2, addrs, dtypes)))
print("")
aAddr1 = [1000, 1002] #dac0, dac1
aVal1 = [4.56, 0.75]
print("eWriteAddresses (" + str(aAddr1) + " " + str(aVal1) + "): " + str(ljm.eWriteAddresses(h, 2, aAddr1, [ljm.constants.FLOAT32, ljm.constants.FLOAT32], aVal1)))
print("")
print("eAddresses: " + str(ljm.eAddresses(h, 2, addrs, dtypes, writes, [1]*2, [0, 0, 0])))
print("")

ljm.eWriteNameArray(h, "DAC0", 2, [2.3, 4.8])
print("eWriteNameArray (DAC0, 2, [2.3 4.8])")
print("eReadNameArray (DAC0, 2): " + str(ljm.eReadNameArray(h, "DAC0", 2)))

print("")

ljm.eWriteAddressArray(h, 1000, ljm.constants.FLOAT32, 2, [0.2, 2.6])
print("eWriteAddressArray (1000, FLOAT32, 2, [0.2 2.6])")
print("eReadAddressArray (1000, FLOAT32, 2): " + str(ljm.eReadAddressArray(h, 1000, ljm.constants.FLOAT32, 2)))

print("\n--- Conversion tests --------------\n")
offset = 0
num = 3

arr = [2.3, 1.6, 5.6, 6543.943] #look into more
retArr = ljm.float32ToByteArray(arr)
print(arr)
print("float32ToByteArray: " + str(retArr))
print("byteArrayToFLOAT32: " + str(ljm.byteArrayToFLOAT32(retArr)))
print("")

arr = [50000, 16, 500, 45, 999, 11111, 656565262626464] #look into more
retArr = ljm.uint16ToByteArray(arr + [46546])
print(arr)
print("uint16ToByteArray: " + str(retArr))
print("byteArrayToUINT16: " + str(ljm.byteArrayToUINT16(retArr)))
print("")

arr = [1000, 100000, 1, 0, 3213, 432]
retArr = ljm.uint32ToByteArray(arr)
print(arr)
print("uint32ToByteArray: " + str(retArr))
print("d.byteArrayToUINT32: " + str(ljm.byteArrayToUINT32(retArr)))
print("")

arr = [-1, 2, -98, -546543, 9387490]
retArr = ljm.int32ToByteArray(arr)
print(arr)
print("int32ToByteArray: " + str(retArr))
print("byteArrayToINT32: " + str(ljm.byteArrayToINT32(retArr)))
print("")

print("\n--- Names tests --------------\n")

print("namesToAddresses: " + str(ljm.namesToAddresses(2, ["AIN0", "AIN8"])))
print("nameToAddress: " + str(ljm.nameToAddress("DAC0")))
nam = "DAC0"
val1 = 3.3
print("eWriteName (" + str(nam) + " " + str(val1) + "): " + str(ljm.eWriteName(h, nam, val1)))
print("eReadName:", ljm.eReadName(h, "AIN0"))
aNam = ["DAC0", "DAC1"]
aVal1 = [1.0, 4.0]
print("eWriteNames (" + str(aNam) + " " + str(aVal1) + "): " + str(ljm.eWriteNames(h, 2, aNam, aVal1)))
print("eReadNames:" + str(ljm.eReadNames(h, 2, ["AIN0", "AIN1"])))
print("eNames: " + str(ljm.eNames(h, 3, ["AIN0", "AIN1", "AIN3"], [ljm.constants.READ, ljm.constants.READ, ljm.constants.READ], [1, 2, 1], [0, 0, 0, 0])))

print("\n--- Other tests --------------\n")

name = "DEVICE_NAME_DEFAULT"
string = "My_T7"
print("eWriteNameString (skip): " + name + " " + string)
#ljm.eWriteNameString(h, name, string)
print("eReadNameString: " + ljm.eReadNameString(h, name))

addr = 60500
print("eWriteAddressString (skip): " + str(addr) + " " + string)
#ljm.eWriteAddressString(h, addr, string)
print("eReadAddressString: " + ljm.eReadAddressString(h, addr))

tcType = ljm.constants.ttK
tcVolts = 0.001203 #about 303.15 K
cjTempK = 273.15#293.15 #about what we want
print("\ntcVoltsToTemp (k type, " + str(tcVolts) + " V or ~303.15 Kelvin, cj = " + str(cjTempK) + " K): " + str(ljm.tcVoltsToTemp(tcType, tcVolts, cjTempK)))


ipnum = 0
ipstr = "192.168.1.89"
ipnum = ljm.ipToNumber(ipstr)
print("\nIPToNumber: " + ipstr + " : " + str(ipnum))
print("numberToIP: " + ljm.numberToIP(ipnum))

macnum = 0
macstr = "E0:69:95:C1:45:12" #E0-69-95-C1-45-12 (E06995C14512)
macnum = ljm.macToNumber(macstr)
print("MACToNumber: " + macstr + " : " + str(macnum))
print("numberToMAC: " + ljm.numberToMAC(macnum))

print("\nloadConfigurationFile: default")
ljm.loadConfigurationFile("default")

#Get the current path to reload it
pStr = ljm.readLibraryConfigStringS(ljm.constants.MODBUS_MAP_CONSTANTS_FILE)
#pStr = str(pStr.replace("ljm_constants.json", ""))

print("loadConstantsFromFile " + pStr)
ljm.loadConstantsFromFile(pStr)

to = 1500 #in ms
ljm.writeLibraryConfigS(ljm.constants.SEND_RECEIVE_TIMEOUT_MS, to)
print("\nwriteLibraryConfigS LJM_SEND_RECEIVE_TIMEOUT_MS: " + str(to))
print("readLibraryConfigS LJM_SEND_RECEIVE_TIMEOUT_MS:" + str(ljm.readLibraryConfigS(ljm.constants.SEND_RECEIVE_TIMEOUT_MS)))

print("writeLibraryConfigStringS")
ljm.writeLibraryConfigStringS(ljm.constants.DEBUG_LOG_FILE, "ljlogfile0.txt")
print("readLibraryConfigStringS: " + str(ljm.readLibraryConfigStringS(ljm.constants.DEBUG_LOG_FILE)))

t = timeit.Timer(lambda: timeoutTest(h)) #"timeoutTest("+ str(h) + ")", setup="from __main__ import timeoutTest")
print("\nread timeout in sec = " + str(t.timeit(number = 1)))

print("closeAll:" + str(ljm.closeAll()))

print("eReadName (should get an error):")
try:
    print(ljm.eReadName(h, "AIN0"))
except ljm.LJMError:
    e = sys.exc_info()[1]
    print(e)

jsonStr = "{\"address\":0, \"name\":\"AIN#(0:254)\", \"type\":\"FLOAT32\", \"devices\":[\"U3\", \"U6\", \"T7\", \"UE9\"], \"readwrite\":\"R\", \"tags\":[\"AIN\"], \"streamable\":true, \"displayname\":[\"Analog In #\"], \"description\":\"Returns the voltage of the specified analog input.\"},\n" + \
   "{\"address\":1000, \"name\":\"DAC#(0:1)\", \"type\":\"FLOAT32\", \"devices\":[\"U3\", \"U6\", \"T7\", \"UE9\"], \"readwrite\":\"RW\", \"tags\":[\"DAC\"], \"displayname\":[\"Analog Out #\"], \"description\":\"Pass a voltage for the specified analog output.\"},\n";
print("\nloadConstantsFromString \n" + jsonStr)
ljm.loadConstantsFromString(jsonStr)
print("\n----- Test End ----------------\n")