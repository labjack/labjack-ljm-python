import sys
from labjack import ljm
import sd_util


def usage():
    print('Usage: %s file_to_read' % (sys.argv[0]))
    exit()


if len(sys.argv) != 2:
    usage()

handle = sd_util.openDevice()
print(sd_util.readFile(handle, sys.argv[1]))
ljm.close(handle)
