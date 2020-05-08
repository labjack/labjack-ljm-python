import sys
from labjack import ljm
import sd_util


def usage():
    print('Usage: %s [directory]' % (sys.argv[0]))
    exit()


listCwd = None
if len(sys.argv) == 1:
    listCwd = True
elif len(sys.argv) == 2:
    listCwd = False
else:
    usage()

handle = sd_util.openDevice()

if listCwd:
    dirToRead = sd_util.getCWD(handle)
else:
    dirToRead = sys.argv[1]

sd_util.listDirContents(handle, dirToRead)
ljm.close(handle)
