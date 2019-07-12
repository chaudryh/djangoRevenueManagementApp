import os
import sys
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt
import pytz
import time
import math

# sys.path.append('../..')
import django
# from bbu.settings import BASE_DIR, MEDIA_ROOT

os.environ['DJANGO_SETTINGS_MODULE'] = 'bowlero_backend.settings'
django.setup()

from bowlero_backend.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse

from RM.Centers.models.models import *
from RM.Pricing.models.models import *

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class PriceLoadProcessor:

    @classmethod
    def price_load_processor(cls):

        file_path = os.path.join(BASE_DIR, 'RM/Centers/sample/config/clean price.xlsx')

        data = pd.read_excel(file_path)

        for index, row in data.iterrows():

            center_id = row['center']
            center_obj = Centers.objects.get(center_id__exact=center_id)
            shoe_price = row['shoes']
            bowling_price = row['bowling']
            business_date = row['business date'].date()
            dow = DOW_choice[business_date.weekday()][0]

            dayparts_map = {'NP': 'non-prime', 'Prime': 'prime', 'Premium': 'premium'}
            period_label = dayparts_map[row['Category']]

            open_hour_obj = OpenHours.objects.get(center_id__exact=center_id, DOW=dow)
            open_hour = open_hour_obj.open_hour
            end_hour = open_hour_obj.end_hour

            price_start_hour = row['Start']
            price_end_hour = row['End']

            if price_start_hour == 'open':
                start_time = datetime.datetime(business_date.year, business_date.month, business_date.day, open_hour.hour, open_hour.minute)
            elif price_start_hour == '11am':
                start_time = datetime.datetime(business_date.year, business_date.month, business_date.day, 11, 0)
            elif price_start_hour == '4pm':
                start_time = datetime.datetime(business_date.year, business_date.month, business_date.day, 16, 0)
            elif price_start_hour == '8pm':
                start_time = datetime.datetime(business_date.year, business_date.month, business_date.day, 20, 0)

            if price_end_hour == 'cl':
                if end_hour < datetime.time(hour=6):
                    delta = datetime.timedelta(days=1)
                else:
                    delta = datetime.timedelta(days=0)
                end_time = datetime.datetime(business_date.year, business_date.month, business_date.day, end_hour.hour, end_hour.minute) + delta
            elif price_end_hour == '4pm':
                end_time = datetime.datetime(business_date.year, business_date.month, business_date.day, 16, 0)
            elif price_end_hour == '6pm':
                end_time = datetime.datetime(business_date.year, business_date.month, business_date.day, 18, 0)
            elif price_end_hour == '8pm':
                end_time = datetime.datetime(business_date.year, business_date.month, business_date.day, 20, 0)

            delta_ = end_time - start_time
            if delta_ > datetime.timedelta(0):
                product = Product.objects.get(name='bowling')
                product_name = 'bowling'
                # print(business_date)
                # RetailBowlingPrice.objects\
                #     .update_or_create(
                #         business_date=business_date,
                #         start_time=start_time,
                #         end_time=end_time,
                #         center_id=center_obj,
                #     defaults={
                #         'price': round(bowling_price, 2),
                #         'period_label': period_label,
                #         'product': product,
                #         'product_name': product_name
                #     }
                # )
                RetailShoePrice.objects\
                    .update_or_create(
                        business_date=business_date,
                        start_time=start_time,
                        end_time=end_time,
                        center_id=center_obj,
                    defaults={
                        'price': round(shoe_price, 2),
                        'period_label': period_label,
                        'product': product,
                        'product_name': product_name
                    }
                )

                # RetailBowlingPrice.objects\
                #     .filter(
                #         business_date=business_date,
                #         start_time=start_time,
                #         end_time=end_time,
                #         center_id=center_obj)\
                #     .update(
                #         price=round(shoe_price, 2),
                #         period_label=period_label,
                #         product=product,
                #         product_name=product_name
                # )
                # RetailShoePrice.objects.create(
                #     business_date=business_date,
                #     start_time=start_time,
                #     end_time=end_time,
                #     center_id=center_obj,
                #     price=round(shoe_price, 2),
                #     period_label=period_label,
                #     product=product,
                #     product_name=product_name
                # )
                # RetailBowlingPrice.objects.create(
                #     business_date=datetime.date(2018,2,22),
                #     start_time=start_time,
                #     end_time=end_time,
                #     center_id=center_obj,
                #     price=round(bowling_price, 2),
                #     period_label=period_label,
                #     product=product,
                #     product_name=product_name
                # )

        print(data)


if __name__ == "__main__":
    PriceLoadProcessor.price_load_processor()