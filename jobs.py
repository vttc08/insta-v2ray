from flask_apscheduler import APScheduler
import random

scheduler = APScheduler()

def printer():
    print("Running some job.")

# for i in range(1):
#     scheduler.add_job(func=printer, trigger='interval', seconds=-1,id=f"myjob{i}")

# scheduler.add_job(func=printer, trigger='interval', seconds=-1,id=f"myjob1")
# scheduler.add_job(func=printer, trigger='interval', seconds=-1,id=f"myjob2")
# jobs = []
# jobs.append(scheduler.get_job('myjob1'))
# jobs.append(scheduler.get_job('myjob2'))
# scheduler.remove_job('myjob1')
# pass