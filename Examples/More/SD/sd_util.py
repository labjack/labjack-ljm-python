"""
Demonstrates usage of the T7's SD card system.
https://labjack.com/support/datasheets/t-series/sd-card

Relevant Documentation:
 
LJM Library:
    LJM Library Installer
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    Multiple Value Functions(such as eWriteNameByteArray):
        https://labjack.com/support/software/api/ljm/function-reference/multiple-value-functions
    Single Value Functions(such as eReadName):
        https://labjack.com/support/software/api/ljm/function-reference/single-value-functions
 
T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    SD Card(T7 Only):
        https://labjack.com/support/datasheets/t-series/sd-card

"""
import os

from labjack import ljm

QUIET_OPEN = True


def sanitizePath(path):
    """Return the path null-terminator guaranteed to be appended to the end.
    """
    if (path[-1] != '\x00'):
        return "%s\x00" % path
    return path


def openDevice(quiet=QUIET_OPEN):
    """Open a device.

    This is defined in one place as a quick way to configure which device is
    opened for all of the scripts in the SD directory.
    """
    # Open first found LabJack
    handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
    #handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
    #handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

    info = ljm.getHandleInfo(handle)

    if not quiet:
        print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
              "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
              (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

    if info[0] == ljm.constants.dtT4:
        print("The T4 does not support an SD card.")
        print("Exiting now.")
        exit()

    return handle


def getCWD(handle):
    """Returns the SD card system's current working directory as a string.
    """
    # 1) Write a value of 1 to FILE_IO_DIR_CURRENT. The error returned
    #    indicates whether there is a directory loaded as current. No error (0)
    #    indicates a valid directory.
    ljm.eWriteName(handle, "FILE_IO_DIR_CURRENT", 1)

    # 2) Read  FILE_IO_PATH_READ_LEN_BYTES.
    len = int(ljm.eReadName(handle, "FILE_IO_PATH_READ_LEN_BYTES"))

    # 3) Read an array of size FILE_IO_PATH_READ_LEN_BYTES from
    #    FILE_IO_PATH_READ
    nameInBytes = ljm.eReadNameByteArray(handle, "FILE_IO_PATH_READ", len)

    # convert to string
    nameStr = "".join(chr(x) for x in nameInBytes)
    return nameStr


def goToPath(handle, sdPath):
    """Changes the SD card system's current working directory to the given path.
    """
    sdPath = sanitizePath(sdPath)

    sdPathLen = len(sdPath)
    sdPathBytes = bytearray(sdPath, 'ascii')

    # 1) Write the length of the file name (including the null terminator) to
    #    FILE_IO_PATH_WRITE_LEN_BYTES
    ljm.eWriteName(handle, "FILE_IO_PATH_WRITE_LEN_BYTES", sdPathLen)

    # 2) Write the name to FILE_IO_NAME_WRITE (with null terminator)
    ljm.eWriteNameByteArray(handle, "FILE_IO_PATH_WRITE", sdPathLen, sdPathBytes)

    # 3) Write a value to FILE_IO_DELETE to delete the file at the specified
    #    path
    ljm.eWriteName(handle, "FILE_IO_DIR_CHANGE", 1)


def getCurDirContents(handle):
    """Return the current working directory's contents as an iterable.
    """
    # 1) Write a value of 1 to FILE_IO_DIR_FIRST. The error returned indicates
    #    whether anything was found. No error (0) indicates that something was
    #    found. FILE_IO_NOT_FOUND (2960) indicates that nothing was found.
    ljm.eWriteName(handle, "FILE_IO_DIR_FIRST", 1)

    # Loop reading name and properties of one file per iteration
    more_files = True
    dirContents = {}
    while more_files:
        # 2) Read FILE_IO_PATH_READ_LEN_BYTES, FILE_IO_ATTRIBUTES, and
        #    FILE_IO_SIZE_BYTES
        len_file_name_as_bytes = int(
            ljm.eReadName(handle, "FILE_IO_PATH_READ_LEN_BYTES")
        )
        size = (int(ljm.eReadName(handle, "FILE_IO_SIZE_BYTES")))
        attr = (int(ljm.eReadName(handle, "FILE_IO_ATTRIBUTES")))

        # 3) Read an array of size FILE_IO_PATH_READ_LEN_BYTES from
        #    FILE_IO_PATH_READ.
        file_name_as_bytes = ljm.eReadNameByteArray(handle, "FILE_IO_PATH_READ",
                                                    len_file_name_as_bytes)

        # convert to string
        file_name_as_strings = "".join(chr(x) for x in file_name_as_bytes)

        dirContents[file_name_as_strings] = (size, attr)

        # 4) Write a value of 1 to FILE_IO_DIR_NEXT. The error returned
        #    indicates whether anything was found. No error (0) indicates that
        #    there are more items->go back to step 2. FILE_IO_INVALID_OBJECT
        #    (2809) and potentially error code FILE_IO_NOT_FOUND (2960)
        #    indicates that there are no more items->Done.
        try:
            ljm.eWriteName(handle, "FILE_IO_DIR_NEXT", 1)
        except:
            more_files = False

    return dirContents


def readFile(handle, sdPath):
    """Return the file contents of the specified path as a string
    """
    sdPath = sanitizePath(sdPath)

    path, filename = os.path.split(sdPath)

    if path:
        raise ValueError('cannot accept a file path that is not in the cwd')

        # path = sanitizePath(path)
        # goToPath(handle, path)
        # This would need to be improved by adding a try/finally so that
        # readFile returns to the cwd before readFile was called

    dir_contents = getCurDirContents(handle)

    # Get file size from the directory contents
    try:
        fileSize = dir_contents[filename][0]
    except KeyError as excep:
        raise ValueError('File not found: %s' % (sdPath))

    # 1) Write the length of the file name to FILE_IO_PATH_WRITE_LEN_BYTES (add
    #    1 for the null terminator);
    filename_len = len(filename)
    ljm.eWriteName(handle, "FILE_IO_PATH_WRITE_LEN_BYTES", filename_len)

    # 2) Write the name to FILE_IO_NAME_WRITE (with null terminator)
    filenameBytes = sdPath.encode()
    ljm.eWriteNameByteArray(handle, "FILE_IO_PATH_WRITE", filename_len,
                            filenameBytes)

    # 3) Write any value to FILE_IO_OPEN
    ljm.eWriteName(handle, "FILE_IO_OPEN", 1)

    # 4) Read file data from FILE_IO_READ (using the size from FILE_IO_SIZE)
    fileDataBytes = ljm.eReadNameByteArray(handle, "FILE_IO_READ", fileSize)

    # 5) Write a value of 1 to FILE_IO_CLOSE
    ljm.eWriteName(handle, "FILE_IO_CLOSE", 1)

    # Convert data bytes to string
    fileData = "".join(chr(x) for x in fileDataBytes)
    return fileData


def printDiskInfo(handle):
    """Prints disk info.
    """
    aNames = ["FILE_IO_DISK_SECTOR_SIZE_BYTES",
              "FILE_IO_DISK_SECTORS_PER_CLUSTER",
              "FILE_IO_DISK_TOTAL_CLUSTERS",
              "FILE_IO_DISK_FREE_CLUSTERS"]
    numFrames = len(aNames)
    results = ljm.eReadNames(handle, numFrames, aNames)

    # totalSize = sector_size * sectors_per_cluster * total_clusters (in bytes)
    totalSize = results[0] * results[1] * results[2]
    # freeSize = sector_size * sectors_per_cluster * free_clusters (in bytes)
    freeSize = results[0] * results[1] * results[3]
    print("%f megabytes free of %f total megabytes." %
          (freeSize/1048576, totalSize/1048576))


def listDirContents(handle, sdPath="/\x00"):
    """Prints the contents of the specified directory.
    """
    # Save starting directory to later return here.
    startingDirectory = getCWD(handle)

    sdPath = sanitizePath(sdPath)

    # Navigate to specified/default directory
    goToPath(handle, sdPath)

    # Get and print contents of the directory
    if sdPath == "/\x00":
        print("Root Directory Contents:")
    else:
        print("%s Directory Contents:" % (sdPath))

    dirContents = getCurDirContents(handle)

    # Print results
    print("%40.40s  %9.9s  %9s" % ("Name\x00", "Type", "Size"))
    for key in dirContents.keys():
        # Check 4 or 5 bit
        if dirContents[key][1] & (1 << 5):
            type = "File"
        else:
            if dirContents[key][1] & (1 << 4):
                type = "Folder"
            else:
                type = "Other"

        if type == "File":
            print("%40.40s  %9.9s  %9d bytes" %
                  (key, type, dirContents[key][0]))
        else:
            print("%40.40s  %9.9s" % (key, type))

    # Return to the starting directory
    goToPath(handle, startingDirectory)


def deleteFile(handle, sdPath):
    """Removes the specified file from the SD card.
    """
    sdPath = sanitizePath(sdPath)
    sdPathLen = len(sdPath)
    sdPathBytes = sdPath.encode()

    # 1) Write the length of the file name (including the null terminator) to
    #    FILE_IO_PATH_WRITE_LEN_BYTES
    ljm.eWriteName(handle, "FILE_IO_PATH_WRITE_LEN_BYTES", sdPathLen)

    # 2) Write the name to FILE_IO_NAME_WRITE (with null terminator)
    ljm.eWriteNameByteArray(handle, "FILE_IO_PATH_WRITE", sdPathLen,
                            sdPathBytes)

    print("Deleting file at %s" % (sdPath))
    # 3) Write a value to FILE_IO_DELETE to delete the file at the specified
    #    path
    ljm.eWriteName(handle, "FILE_IO_DELETE", 1)

    print("Successfully deleted file.")


def exampleProgram():
    handle = openDevice(quiet=False)
    printDiskInfo(handle)
    listDirContents(handle)
    ljm.close(handle)


if __name__ == '__main__':
    exampleProgram()
