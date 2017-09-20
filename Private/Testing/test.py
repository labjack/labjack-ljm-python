from repeating_timer import RepeatingTimer
from repeating_timer import RepeatingTimer2
import time, sys

# Select the time function based on Python version and operating system.
# Use timenow for time afterwards.
if (sys.version_info < (3, 3)):
    # Python version < 3.3
    if sys.platform.startswith("win32"):
        # Windows
        get_time = time.clock
    else:
        # Linux/Mac
        get_time = time.time
else:
    # Python version >= 3.3
    get_time = time.perf_counter

TIME_RUN = 5
START = get_time()

def f():
    time = get_time()
    print("   %.4f" % (time))
    f.prev = time

f.prev = 0
    
rt = RepeatingTimer(0.001, f)
rt.start()
#print("----%f" % rt.get_start_time())

time.sleep(TIME_RUN)

rt.stop()

time.sleep(1)

rt = RepeatingTimer2(1.0, f)
rt.start()
#print("----%f" % rt.get_start_time())

time.sleep(TIME_RUN)

rt.stop()
time.sleep(1)