import sys
from labjack import ljm
import sd_util


def usage():
    print('Usage: %s directory' % (sys.argv[0]))
    exit()


if len(sys.argv) != 2:
    usage()

handle = sd_util.openDevice()
sd_util.goToPath(handle, sys.argv[1])
ljm.close(handle)
