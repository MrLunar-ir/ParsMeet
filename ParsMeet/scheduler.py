import threading
import time

class Job:
    def __init__(self, func, interval=None, at=None, once=False, args=None, kwargs=None):
        self.func = func
        self.interval = interval
        self.at = at
        self.once = once
        self.args = args or []
        self.kwargs = kwargs or {}
        self.last_run = 0
        self.next_run = 0
        self.active = True
        self._compute_next()

    def _compute_next(self):
        now = time.time()
        if self.interval:
            self.next_run = now + self.interval
        elif self.at:
            parts = self.at.split(":")
            hour, minute = int(parts[0]), int(parts[1])
            local = time.localtime(now)
            target = time.mktime((local.tm_year, local.tm_mon, local.tm_mday, hour, minute, 0, 0, 0, -1))
            if target <= now:
                target += 86400
            self.next_run = target

    def due(self):
        return self.active and time.time() >= self.next_run

    def run(self):
        try:
            self.func(*self.args, **self.kwargs)
        except Exception as e:
            print(f"Scheduler error: {e}")
        self.last_run = time.time()
        if self.once:
            self.active = False
        else:
            self._compute_next()

class EveryBuilder:
    def __init__(self, scheduler, seconds):
        self.scheduler = scheduler
        self.seconds = seconds

    def do(self, func, *args, **kwargs):
        job = Job(func, interval=self.seconds, args=args, kwargs=kwargs)
        self.scheduler.add(job)
        return job

class AtBuilder:
    def __init__(self, scheduler, at_time):
        self.scheduler = scheduler
        self.at_time = at_time

    def do(self, func, *args, **kwargs):
        job = Job(func, at=self.at_time, args=args, kwargs=kwargs)
        self.scheduler.add(job)
        return job

class Scheduler:
    def __init__(self):
        self.jobs = []
        self._thread = None
        self._stop = False
        self._lock = threading.Lock()

    def every(self, interval_str):
        return EveryBuilder(self, self._parse_interval(interval_str))

    def at(self, time_str):
        return AtBuilder(self, time_str)

    def once(self, delay_seconds, func, *args, **kwargs):
        job = Job(func, interval=delay_seconds, once=True, args=args, kwargs=kwargs)
        self.add(job)
        return job

    def add(self, job):
        with self._lock:
            self.jobs.append(job)

    def remove(self, job):
        with self._lock:
            if job in self.jobs:
                self.jobs.remove(job)

    def clear(self):
        with self._lock:
            self.jobs.clear()

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop = False
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop = True

    def _loop(self):
        while not self._stop:
            with self._lock:
                jobs = list(self.jobs)
            for job in jobs:
                if job.due():
                    job.run()
            time.sleep(1)

    @staticmethod
    def _parse_interval(s):
        s = s.strip().lower()
        parts = s.split()
        if len(parts) == 2:
            num = int(parts[0])
            unit = parts[1]
        elif len(parts) == 1:
            num = int(parts[0])
            unit = "second"
        else:
            return 60
        if unit.startswith("sec"):
            return num
        if unit.startswith("min"):
            return num * 60
        if unit.startswith("hour"):
            return num * 3600
        if unit.startswith("day"):
            return num * 86400
        return num