from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig


class CurConfig(AppConfig):
    name = 'cur'


    def ready(self):
        pass
        # from cur.tasks import run
        # scheduler = BackgroundScheduler()
        # scheduler.add_job(run, 'interval', hours=1)
        # scheduler.start()
