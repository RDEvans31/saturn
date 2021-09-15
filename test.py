from scheduler import Scheduler
import scheduler
import datetime as dt

def testjob():
    print('running')

schedule=Scheduler(dt.timezone.utc)

schedule.hourly(dt.time(second=0), testjob)

while True:
    schedule.exec_jobs()

