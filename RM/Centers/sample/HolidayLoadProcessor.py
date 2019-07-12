import os
import sys
import numpy as np
import pandas as pd
import re
import datetime as dt
import pytz
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'bowlero_backend.settings'
django.setup()

from bowlero_backend.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse

from RM.EventCalendar.models.models import *

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class HolidayLoadProcessor:

    @classmethod
    def holiday_load_processor(cls):

        file_path = os.path.join(BASE_DIR, 'RM/Centers/sample/config/US Holidays.csv')

        data = pd.read_csv(file_path)
        for index, row in data.iterrows():
            start = row['Date']
            start = UDatetime.datetime_str_init(start)
            end = UDatetime.datetime_str_init(None, start, dt.timedelta(days=1))

            events = Event.objects.update_or_create(
                event_id=row['Id'],
                defaults={
                    'event_name': row['Holiday'],
                    'start': start,
                    'end': end,
                    'all_day': True
                })


if __name__ == '__main__':
    HolidayLoadProcessor.holiday_load_processor()

