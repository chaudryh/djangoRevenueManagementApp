import os
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt
import pytz
import time

from bowlero_backend.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse

from ..models.models import *

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class CentersLoadProcessor:

    @classmethod
    def centers_load_processor(cls):

        file_path = os.path.join(BASE_DIR, 'media/RM/Centers/centers.xlsx')

        data = pd.read_excel(file_path)
        # print(data)
        for index, row in data.iterrows():

            center = Centers.objects.update_or_create(
                center_id=row['Center'],
                defaults={
                    'brand': row['Brand'],
                    'region': row['Region'],
                    'district': row['District'],
                    'center_name': row['Center Name'],
                    'status': row['Center Status'],
                    'time_zone': row['Time Zone'],
                    'address': row['ADDRESS'],
                    'city': row['CITY'],
                    'state': row['STATE'],
                    'zipcode': row['ZIP'],
                    'weekday_prime': row['Weekend Premium'],
                    'weekend_premium': row['Weekday Prime'],
                    'tier': row['Tier'],
                })

            cls.openhours_load_processor(center[0], 'mon',row['Monday'])
            cls.openhours_load_processor(center[0], 'tue', row['Tuesday'])
            cls.openhours_load_processor(center[0], 'wed', row['Wednesday'])
            cls.openhours_load_processor(center[0], 'thu', row['Thursday'])
            cls.openhours_load_processor(center[0], 'fri', row['Friday'])
            cls.openhours_load_processor(center[0], 'sat', row['Saturday'])
            cls.openhours_load_processor(center[0], 'sun', row['Sunday'])

    @classmethod
    def openhours_load_processor(cls, center, dow, time_str):

        regex = re.compile(r'(\s*T\s*/\s*)?'
                           r'((?P<start_hour>\d{1,2})?\s*(?P<start_para1>\w{0,2})?):?'
                           r'((?P<start_min>\d{1,2})?\s*(?P<start_para2>\w{0,2})?)'
                           r'\s*-\s*'
                           r'((?P<end_hour>\d{1,2})?\s*(?P<end_para1>\w{0,2})?):?'
                           r'((?P<end_min>\d{1,2})?\s*(?P<end_para2>\w{0,2})?).*')
        parts = regex.match(time_str)
        if parts:
            parts = parts.groupdict()
        else:
            return None

        # parse time parameter
        AM = ['a', 'A', 'am', 'Am', 'AM']
        PM = ['p', 'P', 'pm', 'Pm', 'PM']

        if parts['start_para1'] in AM or parts['start_para2'] in AM:
            start_para = 'AM'
        elif parts['start_para1'] in PM or parts['start_para2'] in PM:
            start_para = 'PM'
        else:
            start_para = None

        if parts['end_para1'] in AM or parts['end_para2'] in AM:
            end_para = 'AM'
        elif parts['end_para1'] in PM or parts['end_para2'] in PM:
            end_para = 'PM'
        else:
            end_para = None

        # init start timestamp and end timestamp
        start_hour, start_min = cls.str_to_int(parts['start_hour']), cls.str_to_int(parts['start_min'])
        end_hour, end_min = cls.str_to_int(parts['end_hour']), cls.str_to_int(parts['end_min'])

        if  6 <= end_hour and end_hour < 12:
            overnight = False
        else:
            overnight = True

        # change time
        if start_hour == 12 and start_para == 'AM':
            start_hour = 0
        elif start_hour == 12 and start_para == 'PM':
            start_hour = 12
        elif start_para == 'PM':
            start_hour += 12

        if end_hour == 12 and end_para == 'AM':
            end_hour = 0
        elif end_hour == 12 and end_para == 'PM':
            end_hour = 12
        elif end_para == 'PM':
            end_hour += 12

        start = datetime.time(hour=start_hour, minute=start_min)
        end = datetime.time(hour=end_hour, minute=end_min)

        OpenHours.objects.update_or_create(
                center_id=center,
                DOW=dow,
                defaults={
                    'open_hour': start,
                    'end_hour': end,
                    'overnight': overnight,
                })

        return JsonResponse({})

    @staticmethod
    def str_to_int(string):
        if string:
            string = int(string)
        else:
            string = 0
        return string

