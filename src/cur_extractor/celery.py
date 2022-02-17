import os

from celery import Celery
from celery.schedules import solar, crontab

from cur_extractor.Config import Config as configure

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cur_extractor.settings')
app = Celery('cur_extractor')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
app.conf.beat_schedule = {
    # Default executes every hour
    'run_extractor': {
        'task': 'cur.tasks.run',
        'schedule': crontab(
            minute= configure.BEAT_MINUTE or '0',
            hour= configure.BEAT_HOUR or '*',
            day_of_month= configure.BEAT_DAY_OF_WEEK or '*',
            month_of_year= configure.BEAT_MONTH_OF_YEAR or '*',
            day_of_week= configure.BEAT_DAY_OF_MONTH or '*'
        ),
        'args': (),
    },
}
