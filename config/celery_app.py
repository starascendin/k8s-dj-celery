import os

from celery import Celery
from celery.schedules import crontab
# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

print("#DEBUG CElRY -- adding celery_app")
app = Celery("aininjas")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


# BL: for some reason this only works in prod and not local?
app.conf.beat_schedule = {
    # 'every-5min-pull-transcribe-job': {
    #     'task': 'content_process.task_dl_transcripts_and_format',
    #     'schedule': crontab(minute="*/5", hour="*"),
    # },
    'every-1day-scrape-twitter': {
        'task': 'tweetscrape.task_daily_snap',
        'schedule': crontab(
            hour="5", minute="0"
            # minute="*/10", hour="*"
            ),
    }
}

