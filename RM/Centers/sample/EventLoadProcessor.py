import os
import sys
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt, timedelta as td
import pytz
import time
import math

# sys.path.append('../..')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
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

from DAO.DataDAO import *

EST = pytz.timezone(TIME_ZONE)


class EventLoadProcessor:

    start = dt(2018, 7, 10)
    end = dt.now() + td(days=14)

    @classmethod
    def price_tier_load_processor(cls):

        file_path = os.path.join(BASE_DIR, 'RM/Centers/sample/config/events.xlsx')
        records = pd.read_excel(file_path, 'bowling tier table')
        records = pd.melt(records, id_vars=['Tier', 'order'], var_name='product', value_name='price')
        for index, row in records.iterrows():
            product_obj = Product.objects.get(product_name=row['product'])

            PricingTierTable.objects.update_or_create(
                # DOW=row['Day'],
                # time=row['Time'],
                # period_label=row['Category'],
                tier=row['Tier'],
                product_id=product_obj,
                product_name=product_obj.product_name,
                # center_type=center_type,
                defaults={
                    'price': round(float(row['price']), 2),
                    'order': row['order']
                }
            )

    @classmethod
    def event_productopt_init(cls):

        start = dt(2018, 1, 1)
        center_objs = Centers.objects.filter(status='open').exclude(bowling_event_tier=None)
        product_list = [
                        '3001', '3002', '3003', '3004', '3005', '3006', '3007', '3101',
                        '3201', '3202', '3203', '3204', '3205', '3206', '3207', '3208', '3209'
                        ]

        for center_obj in center_objs:
            for product_id in product_list:
                product_obj = Product.objects.get(product_id=product_id)
                ProductOpt.objects.update_or_create(
                    product_id=product_obj,
                    center_id=center_obj,
                    start=start,
                    end=None,
                    defaults={
                        'opt': 'In',
                    }
                )

        return

    @classmethod
    def event_bowling_price_init(cls):

        to_date_range = UDatetime.date_range(cls.start, cls.end)
        product_ids = ['3001', '3002', '3003', '3004', '3005', '3006', '3007']

        # remove previous records
        # ProductPrice.objects.filter(product_id__in=product_ids).delete()

        center_objs = Centers.objects.filter(status='open').exclude(bowling_event_tier=None)
        center_records = pd.DataFrame.from_records(center_objs.values('center_id',
                                                                      'bowling_event_tier'
                                                                      ))

        centers = center_records['center_id'].tolist()

        center_records['bowling_event_tier'] = center_records['bowling_event_tier'].apply(lambda x: str(int(float(x))) if x else x)
        center_records.rename({'bowling_event_tier': 'tier'}, axis=1, inplace=True)

        tier_objs = PricingTierTable.objects.filter(product_id__report_type='Event Bowling')
        tier_records = pd.DataFrame.from_records(tier_objs.values('product_id',
                                                                  'tier',
                                                                  'price'
                                                                  ))

        price_records = center_records.join(tier_records.set_index(['tier']),
                                         on=['tier'], how='left')

        to_records_list = [
            {'center_id': center_id, 'product_id': product_id, 'date': date,
             'DOW': DOW_choice[date.weekday()][0]}
            for center_id in centers
            for product_id in product_ids
            for date in to_date_range
        ]
        to_records = pd.DataFrame(to_records_list)

        # get product schedule
        productschedule_obj = ProductSchedule.objects.filter(product_id__product_id__in=product_ids,
                                                             status='active')
        productschedule_records = pd.DataFrame.from_records(productschedule_obj.values('product_id__product_id',
                                                                                       'DOW'))
        productschedule_records.rename({'product_id__product_id': 'product_id'}, axis=1, inplace=True)
        productschedule_records.drop_duplicates(['product_id', 'DOW'], inplace=True)
        productschedule_records['available'] = True

        to_records = to_records.join(productschedule_records.set_index(['product_id', 'DOW']),
                                     on=['product_id', 'DOW'], how='left')

        to_records = to_records.where((pd.notna(to_records)), False)
        to_records = to_records[to_records['available']]
        if to_records.empty:
            return

        to_records = to_records.join(price_records.set_index(['center_id', 'product_id']),
                                     on=['center_id', 'product_id'], how='left')

        # Load into database
        for index, row in to_records.iterrows():
            center_obj = Centers.objects.get(center_id=row['center_id'])
            product_obj = Product.objects.get(product_id=row['product_id'])

            ProductPrice.objects \
                .update_or_create(
                    date=row['date'],
                    DOW=row['DOW'],
                    center_id=center_obj,
                    product_id=product_obj,
                    defaults={
                        'price': round(row['price'], 2),
                        'perpetual': True,
                        'product_name': product_obj.product_name,
                    }
                )

    @classmethod
    def event_shoe_price_init(cls):

        to_date_range = UDatetime.date_range(cls.start, cls.end)
        product_ids = ['3101']

        center_objs = Centers.objects.filter(status='open').exclude(bowling_event_tier=None)
        center_records = pd.DataFrame.from_records(center_objs.values('center_id',
                                                                      'bowling_event_tier'
                                                                      ))

        centers = center_records['center_id'].tolist()

        to_records_list = [
            {'center_id': center_id, 'product_id': product_id, 'date': date,
             'DOW': DOW_choice[date.weekday()][0]}
            for center_id in centers
            for product_id in product_ids
            for date in to_date_range
        ]
        to_records = pd.DataFrame(to_records_list)

        # get last price
        if not product_ids:
            return
        last_price_records = DataDAO.LastPrice.get_last_price(['115'], centers, cls.start.date())
        if not last_price_records.empty:
            last_price_records = last_price_records[['center_id', 'product_id', 'price']]
            last_price_records['product_id'] = '3101'

        to_records = to_records.join(last_price_records.set_index(['center_id', 'product_id']),
                                     on=['center_id', 'product_id'], how='left')
        to_records.dropna(subset=['price'], inplace=True)
        # Load into database
        for index, row in to_records.iterrows():
            center_obj = Centers.objects.get(center_id=row['center_id'])
            product_obj = Product.objects.get(product_id=row['product_id'])

            ProductPrice.objects \
                .update_or_create(
                    date=row['date'],
                    DOW=row['DOW'],
                    center_id=center_obj,
                    product_id=product_obj,
                    defaults={
                        'price': round(row['price'], 2),
                        'perpetual': True,
                        'product_name': product_obj.product_name,
                    }
                )

        return

    @classmethod
    def event_packages_price_init(cls):

        to_date_range = UDatetime.date_range(cls.start, cls.end)
        product_ids = ['3201', '3202', '3203', '3204', '3205', '3206', '3207', '3208', '3209']

        center_objs = Centers.objects.filter(status='open').exclude(bowling_event_tier=None)
        center_records = pd.DataFrame.from_records(center_objs.values('center_id',
                                                                      'bowling_event_tier'
                                                                      ))

        centers = center_records['center_id'].tolist()

        to_records_list = [
            {'center_id': center_id, 'product_id': product_id, 'date': date,
             'DOW': DOW_choice[date.weekday()][0]}
            for center_id in centers
            for product_id in product_ids
            for date in to_date_range
        ]
        to_records = pd.DataFrame(to_records_list)

        # get last price
        if not product_ids:
            return

        file_path = os.path.join(BASE_DIR, 'RM/Centers/sample/config/events.xlsx')
        price_records = pd.read_excel(file_path, 'packages')
        price_records = pd.melt(price_records, id_vars=['center_id'], var_name='product_id', value_name='price')
        price_records['product_id'] = price_records['product_id'].astype(str)
        price_records['center_id'] = price_records['center_id'].astype(str)

        to_records = to_records.join(price_records.set_index(['center_id', 'product_id']),
                                     on=['center_id', 'product_id'], how='left')

        to_records.dropna(subset=['price'], inplace=True)
        # Load into database
        for index, row in to_records.iterrows():
            center_obj = Centers.objects.get(center_id=row['center_id'])
            product_obj = Product.objects.get(product_id=row['product_id'])

            ProductPrice.objects \
                .update_or_create(
                    date=row['date'],
                    DOW=row['DOW'],
                    center_id=center_obj,
                    product_id=product_obj,
                    defaults={
                        'price': round(row['price'], 2),
                        'perpetual': True,
                        'product_name': product_obj.product_name,
                    }
                )

        return


if __name__ == "__main__":
    loader = input('Please give the loader type('
                   '1:load event tier price; '
                   '2:load event product opt; '
                   '3:init event bowling price; '
                   '4:init event shoe price; '
                   '5:init event packages price; '
                   '):')
    if int(loader) == 1:
        EventLoadProcessor.price_tier_load_processor()
    elif int(loader) == 2:
        EventLoadProcessor.event_productopt_init()
    elif int(loader) == 3:
        EventLoadProcessor.event_bowling_price_init()
    elif int(loader) == 4:
        EventLoadProcessor.event_shoe_price_init()
    elif int(loader) == 5:
        EventLoadProcessor.event_packages_price_init()

