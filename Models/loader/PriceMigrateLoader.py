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
from RM.Food.models.models import *
from Models.models.models import *

from utils.UDatetime import UDatetime
from DAO.DataDAO import *

EST = pytz.timezone(TIME_ZONE)


class PriceMigrateLoader:

    start = dt(2018, 1, 1)

    @classmethod
    def product_migrate_loader(cls):

        file_path = os.path.join(BASE_DIR, 'Models/loader/files/change report.xlsx')
        change_records = pd.read_excel(file_path)
        change_records['Effective Start'] = pd.to_datetime(change_records['Effective Start'])
        change_records['Date Time'] = pd.to_datetime(change_records['Date Time'])

        # change_records = change_records.where((pd.notnull(product_records)), None)

        product_ids = ['108', '110', '111', '113', '114', '115']
        center_ids = list(Centers.objects.filter(status='open').values_list('center_id', flat=True))

        to_records_list = [
            {'center_id': center_id, 'product_id': product_id}
            for center_id in center_ids
            for product_id in product_ids
        ]
        to_records = pd.DataFrame(to_records_list)

        last_price_records = DataDAO.LastPrice.get_last_price(product_ids, center_ids)
        to_records = to_records.join(last_price_records.set_index(['center_id', 'product_id']),
                                     on=['center_id', 'product_id'], how='left')
        to_records = to_records[pd.notnull(to_records['price'])]

        for index, row in change_records.iterrows():
            start_row = row['Effective Start']
            product_obj = Product.objects.get(product_id=row['Prod Id'])
            user = User.objects.get(username=row['User'])
            center_obj = Centers.objects.get(center_id=row['Center'])
            action_time = row['Date Time']
            price_old = round(row['Old Price'], 2)
            price_new = round(row['New Price'], 2)

            ProductPriceChange.objects \
                .update_or_create(
                start=cls.start,
                end=start_row,
                center_id=center_obj,
                product_id=product_obj,
                action_user=user,
                action_time=action_time,
                defaults={
                    'price': price_old,
                    'perpetual': False,
                    'product_name': product_obj.product_name,
                }
            )

            ProductPriceChange.objects \
                .update_or_create(
                start=start_row,
                end=None,
                center_id=center_obj,
                product_id=product_obj,
                action_user=user,
                action_time=action_time,
                defaults={
                    'price': price_new,
                    'perpetual': True,
                    'product_name': product_obj.product_name,
                }
            )

        for index, row in to_records.iterrows():
            center_id = row['center_id']
            product_id = row['product_id']
            price_obj = ProductPriceChange.objects.filter(center_id=center_id,
                                                          product_id=product_id
                                                          )
            if price_obj.exists():
                continue

            center_obj = Centers.objects.get(center_id=center_id)
            product_obj = Product.objects.get(product_id=product_id)
            ProductPriceChange.objects \
                .update_or_create(
                    start=cls.start,
                    end=None,
                    center_id=center_obj,
                    product_id=product_obj,
                    action_time=cls.start,
                    defaults={
                        'price': round(row['price'], 2),
                        'perpetual': True,
                        'product_name': product_obj.product_name,
                    }
                )


if __name__ == "__main__":
    PriceMigrateLoader.product_migrate_loader()
    # center_ids = list(Centers.objects.filter(status='open').values_list('center_id', flat=True))
    # product_ids = ['108', '110', '111', '113', '114', '115']
    # data_new = PriceChange.get_last_price(product_ids,
    #                                   center_ids=center_ids,
    #                                   as_of_date=dt(2018, 7, 24).date())
    #
    # data_old = DataDAO.LastPrice.get_last_price(product_ids, center_ids=center_ids,
    #                                                       as_of_date=dt(2018, 7, 24).date())
    # data_new.to_csv('last_price new.csv')
    # data_old.to_csv('last_price old.csv')