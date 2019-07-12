import os
import sys
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt
import pytz
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'bowlero_backend.settings'
django.setup()

from bowlero_backend.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse

from RM.Centers.models.models import *
from RM.Food.models.models import *

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class CentersLoader:

    start = dt(2018, 1, 1)

    @classmethod
    def new_centers_loader(cls):

        file_path = os.path.join(BASE_DIR, 'Models/loader/files/Center list.xlsx')

        data = pd.read_excel(file_path)
        data = data.where((pd.notnull(data)), None)
        data = data[data['new'] == 'yes']

        product_ids = Product.objects \
            .filter(always_opt_in='in') \
            .exclude(report_type='Event') \
            .values_list('product_id', flat=True)
        for index, row in data.iterrows():

            if row['Food Kiosk'] == 'yes':
                row['Food Kiosk'] = True
            elif pd.isna(row['Food Kiosk']):
                row['Food Kiosk'] = False

            # food_menu = Menu.objects.get(name=row['Food Menu'])

            center_obj, create = Centers.objects.update_or_create(
                center_id=row['Center'],
                defaults={
                    'brand': row['Brand'],
                    'region': row['Region'],
                    'district': row['District'],
                    'center_name': row['Center Name'],
                    'status': row['Center Status'],
                    'sale_region': row['Sale Region'],
                    'territory': row['Territory'],
                    'rvp': row['RVP'],
                    'time_zone': row['Time Zone'],
                    'address': row['ADDRESS'],
                    'city': row['CITY'],
                    'state': row['STATE'],
                    'zipcode': row['ZIP'],
                    'latitude': row['Latitude'],
                    'longitude': row['Longitude'],
                    'weekday_prime': row['Weekday Prime'],
                    'weekend_premium': row['Weekend Premium'],
                    'bowling_tier': row['Bowling Tier'],
                    'bowling_event_tier': row['Bowling Event Tier'],
                    'alcohol_tier': row['Alcohol Tier'],
                    'food_tier': row['Food Tier'],
                    'food_menu': row['Food Menu'],
                    'food_kiosk': row['Food Kiosk'],
                    'center_type': row['Center Type'],
                    'sunday_funday_bowling': row['Sunday Funday Bowling'],
                    'sunday_funday_shoes': row['Sunday Funday Shoes'],
                    'monday_mayhem': row['Monday Mayhem'],
                    'tuesday_222': row['222 Tuesday'],
                    'college_night_schedule': row['College Night Schedule'],
                    'college_night': row['College Night'],
                    'college_night_wed': row['College Night Wed'],
                    'college_night_thu': row['College Night Thu'],
                    'arcade_type': row['Arcade Type'],
                })

            for product_id in product_ids:
                product_obj = Product.objects.get(product_id=product_id)
                ProductOpt.objects.update_or_create(
                    product_id=product_obj,
                    center_id=center_obj,
                    start=cls.start,
                    end=None,
                    defaults={
                        'opt': 'In',
                    }
                )

    @classmethod
    def centers_loader(cls):

        file_path = os.path.join(BASE_DIR, 'Models/loader/files/Center list.xlsx')

        data = pd.read_excel(file_path)
        data = data.where((pd.notnull(data)), None)

        data['Brand'] = data['Brand'].str.rstrip()
        data['Region'] = data['Region'].str.rstrip()
        data['District'] = data['District'].str.rstrip()
        data['Center Name'] = data['Center Name'].str.rstrip()

        for index, row in data.iterrows():

            if row['Food Kiosk'] == 'yes':
                row['Food Kiosk'] = True
            elif pd.isna(row['Food Kiosk']):
                row['Food Kiosk'] = False

            # food_menu = Menu.objects.get(name=row['Food Menu'])

            center = Centers.objects.update_or_create(
                center_id=row['Center'],
                defaults={
                    'brand': row['Brand'],
                    'region': row['Region'],
                    'district': row['District'],
                    'center_name': row['Center Name'],
                    'status': row['Center Status'],
                    'sale_region': row['Sale Region'],
                    'territory': row['Territory'],
                    'rvp': row['RVP'],
                    'time_zone': row['Time Zone'],
                    'address': row['ADDRESS'],
                    'city': row['CITY'],
                    'state': row['STATE'],
                    'zipcode': row['ZIP'],
                    'latitude': row['Latitude'],
                    'longitude': row['Longitude'],
                    'weekday_prime': row['Weekday Prime'],
                    'weekend_premium': row['Weekend Premium'],
                    'bowling_tier': row['Bowling Tier'],
                    'bowling_event_tier': row['Bowling Event Tier'],
                    'alcohol_tier': row['Alcohol Tier'],
                    'food_tier': row['Food Tier'],
                    'food_menu': row['Food Menu'],
                    'food_kiosk': row['Food Kiosk'],
                    'center_type': row['Center Type'],
                    'sunday_funday_bowling': row['Sunday Funday Bowling'],
                    'sunday_funday_shoes': row['Sunday Funday Shoes'],
                    'monday_mayhem': row['Monday Mayhem'],
                    'tuesday_222': row['222 Tuesday'],
                    'college_night_schedule': row['College Night Schedule'],
                    'college_night': row['College Night'],
                    'college_night_wed': row['College Night Wed'],
                    'college_night_thu': row['College Night Thu'],
                    'arcade_type': row['Arcade Type'],
                    'lane': row['Lane']
                })

            # cls.openhours_load_processor(center[0], 'mon',row['Monday'])
            # cls.openhours_load_processor(center[0], 'tue', row['Tuesday'])
            # cls.openhours_load_processor(center[0], 'wed', row['Wednesday'])
            # cls.openhours_load_processor(center[0], 'thu', row['Thursday'])
            # cls.openhours_load_processor(center[0], 'fri', row['Friday'])
            # cls.openhours_load_processor(center[0], 'sat', row['Saturday'])
            # cls.openhours_load_processor(center[0], 'sun', row['Sunday'])

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


if __name__ == '__main__':
    CentersLoader.new_centers_loader()

