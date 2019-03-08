import sys
from labjack import ljm
import sd_util


def usage():
    print('Usage: %s [directory]' % (sys.argv[0]))
    exit()


list_cwd = None
if len(sys.argv) == 1:
    list_cwd = True
elif len(sys.argv) == 2:
    list_cwd = False
else:
    usage()

handle = sd_util.openDevice()

if list_cwd:
    dir_to_read = sd_util.getCWD(handle)
else:
    dir_to_read = sys.argv[1]

sd_util.listDirContents(handle, dir_to_read)
ljm.close(handle)
