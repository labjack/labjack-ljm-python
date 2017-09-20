import sys
import time
from threading import Timer
from threading import Thread


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


class RepeatingTimer:
    def __init__(self, interval, function, *args, **kwargs):
        self._init(interval, function, True, 0, *args, **kwargs)

    def __init__(self, interval, function, use_thread=True, run_time=0, *args,
                 **kwargs):
        self._init(interval, function, use_thread, run_time, *args, **kwargs)

    def _init(self, interval, function, use_thread, run_time, *args, **kwargs):
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self._is_running = False
        self.use_thread = use_thread
        self._thread = None
        self._start_time = None
        self.run_time = run_time

    def _run(self):
        time_next = self._start_time
        while self._is_running:
            cur_time = get_time()
            #print("%.4f , %.4f" % (cur_time, self.time_next))
            if (self.run_time > 0) and \
               ((cur_time - self._start_time) >= self.run_time):
                self._is_running = False
                pass
            time_changed = False
            while cur_time > time_next:
                time_next += self.interval
                time_changed = True
            if time_changed:
                time.sleep(time_next - cur_time)
                self.function(*self.args, **self.kwargs)
            else:
                pass
                #print("Repeat")

    def start(self):
        self._is_running = True
        self._start_time = get_time()
        print("start_time = %.4f, interval = %.4f" % (self._start_time, self.interval))
        if self.use_thread:
            self._thread = Thread(target=self._run)
            self._thread.start()
        else:
            self._run()

    def get_start_time(self):
        return self._start_time

    def stop(self, timeout=None):
        self._is_running = False
        self._thread.join(timeout)

    def is_running(self):
        return self._is_running

    #def join(self, timeout=None):
    #    self._thread(timeout)

class RepeatingTimer2:
    def __init__(self, interval, function, *args, **kwargs):
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.timer = None
        self.time_next = None
        self.start_time = None

    def _run(self):
        if self.is_running:
            cur_time = get_time()
            while cur_time > self.time_next:
                self.time_next += self.interval
            #self.timer = Timer((self.time_next - cur_time), self._run)
            self.timer = Timer(self.interval, self._run)
            self.timer.start()
            self.function(*self.args, **self.kwargs)

    def start(self):
        self.is_running = True
        self.start_time = get_time()
        self.time_next = self.start_time + self.interval
        self.timer = Timer(self.interval, self._run)
        self.timer.start()

    def get_start_time(self):
        return self.start_time

    def stop(self):
        self.is_running = False
        self.timer.cancel()
