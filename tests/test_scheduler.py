import time
from ParsMeet.scheduler import Scheduler, Job

def test_scheduler_interval_parse():
    s = Scheduler()
    assert s._parse_interval("1 second") == 1
    assert s._parse_interval("2 minutes") == 120
    assert s._parse_interval("1 hour") == 3600

def test_job_due():
    called = []
    job = Job(lambda: called.append(1), interval=0)
    job.next_run = time.time() - 1
    assert job.due() is True
    job.run()
    assert len(called) == 1

def test_scheduler_add_remove():
    s = Scheduler()
    job = Job(lambda: None, interval=60)
    s.add(job)
    assert job in s.jobs
    s.remove(job)
    assert job not in s.jobs