# -*- coding: utf-8 -*-

import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

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
        effective_datetime = datetime.datetime(2018, 1, 1)

        for index, row in data.iterrows():

            center_id = row['center']
            center_obj = Centers.objects.get(center_id__exact=center_id)
            shoe_price = row['shoes']
            bowling_price = row['bowling']
            business_date = row['business date'].date()
            dow = DOW_choice[business_date.weekday()][0]
            overnight = False

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
                    overnight = True
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
                # print(business_date)
                RetailBowlingPriceOld.objects\
                    .update_or_create(
                        effective_datetime=effective_datetime,
                        start_time=start_time.time(),
                        end_time=end_time.time(),
                        center_id=center_obj,
                        DOW=dow,
                        product_name='retail bowling',
                        defaults={
                            'price': round(bowling_price, 2),
                            'period_label': period_label,
                            'status': 'active',
                            'overnight': overnight
                        }
                    )
                RetailShoePriceOld.objects\
                    .update_or_create(
                        effective_datetime=effective_datetime,
                        start_time=start_time.time(),
                        end_time=end_time.time(),
                        center_id=center_obj,
                        DOW=dow,
                        product_name='retail shoes',
                        defaults={
                            'price': round(shoe_price, 2),
                            'period_label': period_label,
                            'status': 'active',
                            'overnight': overnight
                        }
                    )
                Period.objects\
                    .update_or_create(
                        effective_datetime=effective_datetime,
                        start_time=start_time.time(),
                        end_time=end_time.time(),
                        center_id=center_obj,
                        DOW=dow,
                        period_label=period_label,
                        defaults={
                            'status': 'active',
                            'overnight': overnight
                        }
                    )

    @classmethod
    def price_new_load_processor(cls):

        file_path = os.path.join(BASE_DIR, 'RM/Centers/sample/config/clean price.xlsx')

        data = pd.read_excel(file_path)

        for index, row in data.iterrows():
            center_id = row['center']
            center_obj = Centers.objects.get(center_id=center_id)
            center_type = Centers.objects.filter(center_id=center_id).values('center_type')[0]['center_type']
            shoe_price = row['shoes']
            bowling_price = row['bowling']
            business_date = row['business date'].date()
            dow = DOW_choice[business_date.weekday()][0]

            dayparts_map = {'NP': 'non-prime', 'Prime': 'prime', 'Premium': 'premium'}
            period_label = dayparts_map[row['Category']]

            if not center_type or center_type == 'session':
                center_type = 'traditional'

            product_bowling = 'retail {center_type} {period_label} bowling'.format(
                center_type=center_type,
                period_label=period_label
            )
            product_shoe = 'retail shoe'

            product_bowling_obj = Product.objects.get(product_name=product_bowling)
            product_shoe_obj = Product.objects.get(product_name=product_shoe)

            RetailBowlingPrice.objects \
                .update_or_create(
                date=business_date,
                DOW=dow,
                center_id=center_obj,
                product_id=product_bowling_obj,
                product_name=product_bowling,
                defaults={
                    'price': round(bowling_price, 2),
                }
            )
            RetailShoePrice.objects \
                .update_or_create(
                date=business_date,
                DOW=dow,
                center_id=center_obj,
                product_id=product_shoe_obj,
                product_name=product_shoe,
                defaults={
                    'price': round(shoe_price, 2),
                }
            )

    @classmethod
    def price_promos_load_processor(cls):

        week_len = 4

        centers = Centers.objects.all()
        products = ['Sunday Funday Bowling',
                    'Sunday Funday Shoes',
                    'Monday Mayhem AYCB',
                    '222 Tuesday Game',
                    'College night Wed',
                    'College night Thu'
                    ]

        for center in centers:
            for product in products:
                if product == 'Sunday Funday Bowling':
                    price = center.sunday_funday_bowling
                    DOW='sun'
                    product_obj = Product.objects.get(product_name=product)
                    date_range = UDatetime.date_range_by_DOW('sun', week_len=week_len)
                elif product == 'Sunday Funday Shoes':
                    price = center.sunday_funday_shoes
                    DOW = 'sun'
                    product_obj = Product.objects.get(product_name=product)
                    date_range = UDatetime.date_range_by_DOW('sun', week_len=week_len)
                elif product == 'Monday Mayhem AYCB':
                    price = center.monday_mayhem
                    DOW = 'mon'
                    product_obj = Product.objects.get(product_name=product)
                    date_range = UDatetime.date_range_by_DOW('mon', week_len=week_len)
                elif product == '222 Tuesday Game':
                    price = center.tuesday_222
                    DOW = 'tue'
                    product_obj = Product.objects.get(product_name=product)
                    date_range = UDatetime.date_range_by_DOW('tue', week_len=week_len)
                elif product == 'College night Wed':
                    price = center.college_night_wed
                    DOW = 'wed'
                    product_obj = Product.objects.get(product_name=product)
                    date_range = UDatetime.date_range_by_DOW('wed', week_len=week_len)
                elif product == 'College night Thu':
                    price = center.college_night_thu
                    DOW = 'thu'
                    product_obj = Product.objects.get(product_name=product)
                    date_range = UDatetime.date_range_by_DOW('thu', week_len=week_len)
                else:
                    continue

                if not price:
                    continue

                for date in date_range:
                    ProductPrice.objects \
                        .update_or_create(
                            date=date,
                            DOW=DOW,
                            center_id=center,
                            product_id=product_obj,
                            product_name=product_obj.product_name,
                            defaults={
                                'price': round(price, 2),
                            }
                    )

    @classmethod
    def price_retail_bowling_migrate_processor(cls):

        bowling_price_objs = RetailBowlingPrice.objects.filter(product_id__in=ProductChoice.retail_bowling_ids)

        for bowling_price in bowling_price_objs:
            center_obj = bowling_price.center_id
            product_id = bowling_price.product_id.product_id
            dow = bowling_price.DOW
            date = bowling_price.date
            price = bowling_price.price
            perpetual = bowling_price.perpetual

            if product_id in ['101', '104']:
                product_id_new = '108'
            elif product_id in ['103', '106']:
                product_id_new = '113'
            elif product_id in ['102', '105']:
                if dow in ['mon', 'tue', 'wed', 'thu']:
                    product_id_new = '110'
                elif dow in ['fri', 'sat', 'sun']:
                    product_id_new = '111'
                else:
                    continue
            else:
                continue

            product_obj_new = Product.objects.get(product_id=product_id_new)
            RetailBowlingPrice.objects \
                .update_or_create(
                    center_id=center_obj,
                    product_id=product_obj_new,
                    DOW=dow,
                    date=date,
                    price=price,
                    defaults={
                        'product_name': product_obj_new.product_name,
                        'perpetual': perpetual
                    }
                )

    @classmethod
    def price_retail_shoe_migrate_processor(cls):

        shoe_price_objs = RetailShoePrice.objects.filter(product_id__in=ProductChoice.retail_shoe_product_ids)

        for shoe_price in shoe_price_objs:
            center_obj = shoe_price.center_id
            product_id = shoe_price.product_id.product_id
            dow = shoe_price.DOW
            date = shoe_price.date
            price = shoe_price.price
            perpetual = shoe_price.perpetual

            if dow in ['mon', 'tue', 'wed', 'thu']:
                product_ids_new = ['114']
            elif dow in ['sat']:
                product_ids_new = ['115']
            elif dow in ['fri', 'sun']:
                product_ids_new = ['114', '115']
            else:
                continue

            for product_id_new in product_ids_new:
                product_obj_new = Product.objects.get(product_id=product_id_new)
                RetailShoePrice.objects \
                    .update_or_create(
                        center_id=center_obj,
                        product_id=product_obj_new,
                        DOW=dow,
                        date=date,
                        price=price,
                        defaults={
                            'product_name': product_obj_new.product_name,
                            'perpetual': perpetual
                        }
                    )


if __name__ == "__main__":
    loader = input('Please give the loader type(1:bowling/show, 2:promos, 3: retail bowling price migrate '
                   '4: retail shoe price migrate):'
                   )
    # PriceLoadProcessor.price_load_processor()
    if int(loader) == 1:
        PriceLoadProcessor.price_new_load_processor()
    elif int(loader) == 2:
        PriceLoadProcessor.price_promos_load_processor()
    elif int(loader) == 3:
        PriceLoadProcessor.price_retail_bowling_migrate_processor()
    elif int(loader) == 4:
        PriceLoadProcessor.price_retail_shoe_migrate_processor()
