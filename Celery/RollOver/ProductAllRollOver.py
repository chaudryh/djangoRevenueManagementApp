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

from DAO.DataDAO import *

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class ProductRollOver:

    rollover_report_type = ['Retail Bowling', 'Retail Shoe', 'Retail Promos']
    product_rollover_opt_out = ['109', '112']

    @classmethod
    def product_roll_over(cls, rolling_week=2, current_user=None):
        start = UDatetime.now_local().date()
        end = start + rolling_week * timedelta(days=7) - timedelta(days=1)

        current_user = User.objects.get(username='rollover@bowlerocorp.com')

        center_ids = Centers.objects.filter(status='open').values_list('center_id', flat=True)

        # product_ids = Product.objects \
        #     .filter(status='active', report_type__in=cls.rollover_report_type).values_list('product_id', flat=True)
        # product_ids = Product.objects \
        #     .filter(status='active', report_type='Retail Bowling').values_list('product_id', flat=True)
        # product_ids = Product.objects \
        #     .filter(status='active', report_type='Retail Shoe').values_list('product_id', flat=True)
        product_ids = Product.objects \
            .filter(status='active', report_type='Retail Promos').values_list('product_id', flat=True)

        # model = RetailBowlingPrice
        # model = RetailShoePrice
        model = ProductPrice

        product_ids = [product_id for product_id in product_ids if product_id not in cls.product_rollover_opt_out]

        # get last price
        last_price_records = DataDAO.LastPrice.get_last_price(product_ids, center_ids, start, perpetual_only=True)
        if last_price_records.empty:
            return
        last_price_records = last_price_records[['center_id', 'product_id', 'price']]

        # init to_records
        to_date_range = UDatetime.date_range(start, end)

        if not to_date_range:
            return
        to_records_list = [
            {'center_id': center_id, 'product_id': product_id, 'date': date,
             'DOW': DOW_choice[date.weekday()][0]}
            for center_id in center_ids
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

        # Get product opt in / out
        productopt_records = ProductOptGet.get_productopt(product_ids, start, end, center_ids)
        to_records['date'] = to_records['date'].apply(lambda x: str(x))
        productopt_records['date'] = productopt_records['date'].apply(lambda x: str(x))

        to_records = to_records.join(productopt_records.set_index(['center_id', 'product_id', 'date']),
                                     on=['center_id', 'product_id', 'date'], how='left')

        to_records = to_records[(to_records['available']) & (to_records['opt'] == 'In')]

        # get rollover price
        to_records = to_records.join(last_price_records.set_index(['center_id', 'product_id']),
                                     on=['center_id', 'product_id'], how='left')

        # remove overlap
        from_price_obj = model.objects  \
            .filter(
                center_id__in=center_ids,
                product_id__in=product_ids,
                date__range=[start, end]
            )  \
            .exclude(action_user=current_user)
        from_product_record = pd.DataFrame.from_records(from_price_obj.values(
            'center_id',
            'product_id',
            'date',
            'price'
        ))

        if not from_product_record.empty:
            from_product_record.rename({'price': 'current_price'}, inplace=True, axis=1)
            to_records['date'] = to_records['date'].apply(lambda x: str(x))
            from_product_record['date'] = from_product_record['date'].apply(lambda x: str(x))

            result_record = to_records.join(from_product_record.set_index(['center_id', 'product_id', 'date']),
                                            on=['center_id', 'product_id', 'date'], how='left',
                                            )
            result_record = result_record[result_record['current_price'].isnull()]
        else:
            result_record = to_records.copy()

        # remove NA price
        result_record = result_record[~result_record['price'].isna()]

        # remove rollover
        model.objects \
            .filter(
                center_id__in=center_ids,
                product_id__in=product_ids,
                date__range=[start, end],
                action_user=current_user) \
            .delete()

        # add rollover
        for index, row in result_record.iterrows():
            center_obj = Centers.objects.get(center_id=row['center_id'])
            product_obj = Product.objects.get(product_id=row['product_id'])

            model.objects.create(
                date=row['date'],
                DOW=row['DOW'],
                center_id=center_obj,
                product_id=product_obj,
                product_name=product_obj.product_name,
                price=round(row['price'], 2),
                action_user=current_user
            )


if __name__ == '__main__':
    ProductRollOver.product_roll_over()

