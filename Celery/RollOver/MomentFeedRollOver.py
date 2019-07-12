import os
import sys
import numpy as np
import pandas as pd
import re
from datetime import datetime, timedelta
import pytz
import time
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
import django
# from bbu.settings import BASE_DIR, MEDIA_ROOT

os.environ['DJANGO_SETTINGS_MODULE'] = 'bowlero_backend.settings'
django.setup()

from bowlero_backend.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse

from RM.Centers.models.models import *
from RM.Pricing.models.models import *

from utils.UDatetime import UDatetime

from api.MomentFeedAPI import MomentFeedAPI

EST = pytz.timezone(TIME_ZONE)


class MomentFeedRollOver:

    @classmethod
    def momentfeed_roll_over(cls, rolling_week=2, current_user=None):

        current_user = User.objects.get(username='rollover@bowlerocorp.com')

        records = MomentFeedAPI.get_all_centers()

        for index, row in records.iterrows():
            center_obj = Centers.objects.filter(center_id=row['center_id'])
            if center_obj.exists():
                center_obj = center_obj[0]
            else:
                continue

            start = row['start']
            end = row['end']

            if start and end:
                if datetime.time(0, 0) <= end <= datetime.time(4, 0):
                    overnight = True
                else:
                    overnight = False
            else:
                overnight = False

            OpenHours.objects.update_or_create(
                center_id=center_obj,
                DOW=row['dow'],
                defaults={
                    'open_hour': start,
                    'end_hour': end,
                    'overnight': overnight,
                    'action_time': UDatetime.now_local(),
                    'action_user': current_user
                })


if __name__ == '__main__':
    MomentFeedRollOver.momentfeed_roll_over()

