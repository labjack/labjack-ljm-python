import sys
from labjack import ljm
import sd_util


def usage():
    print('Usage: %s file_to_delete' % (sys.argv[0]))
    exit()


if len(sys.argv) != 2:
    usage()

handle = sd_util.openDevice()
sd_util.deleteFile(handle, sys.argv[1])
ljm.close(handle)
