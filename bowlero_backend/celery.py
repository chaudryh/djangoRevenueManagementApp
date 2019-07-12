from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
import os
import sys

try:
    from bowlero_backend.ENV.env import ENV
except:
    ENV = 'LOCAL'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bowlero_backend.settings')
app = Celery('bowlero_backend')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
# app.conf.timezone = 'America/New_York'

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


# time in UTC
app.conf.beat_schedule = {
    'roll_over_retail_bowling': {
        'task': 'Celery.RollOver.tasks.roll_over_retail_bowling',
        'schedule': crontab(day_of_week='sat', minute=0, hour=0),
        'args': (),
    },
    'roll_over_retail_shoe': {
        'task': 'Celery.RollOver.tasks.roll_over_retail_shoe',
        'schedule': crontab(day_of_week='sat', minute=0, hour=1),
        'args': (),
    },
    'roll_over_product': {
        'task': 'Celery.RollOver.tasks.roll_over_product',
        'schedule': crontab(day_of_week='sat', minute=0, hour=2),
        'args': (),
    },
    'roll_over_momentfeed': {
        'task': 'Celery.RollOver.tasks.roll_over_momentfeed',
        'schedule': crontab(minute=0, hour=0),
        'args': (),
    },
    'roll_over_weather': {
        'task': 'Celery.RollOver.tasks.roll_over_weather',
        'schedule': crontab(minute=0, hour=10),
        'args': (),
    },
}

if ENV in ['DEV', 'PROD']:
    prod_beat_schedule = {
        'ServerStatus': {
            'task': 'Celery.ServerStatus.tasks.serverStatus',
            'schedule': crontab(minute=30, hour='11,15,20'),
            'args': (),
        },
    }
    app.conf.beat_schedule.update(prod_beat_schedule)

if ENV in ['PROD']:
    prod_beat_schedule = {
        'email_notice': {
            'task': 'Celery.RollOver.tasks.email_notice',
            'schedule': crontab(minute=0, hour=2),
            'args': (),
        },
    }
    app.conf.beat_schedule.update(prod_beat_schedule)


def is_available_workers():
    result = app.control.inspect().ping()
    if result:
        count = 0
        for key, value in result.items():
            if value['ok'] == 'pong':
                count += 1
        if count >= 1:
            result = True
        else:
            result = False
    else:
        result = False
    return result
