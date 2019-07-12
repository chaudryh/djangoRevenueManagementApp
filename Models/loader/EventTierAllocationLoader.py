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
from Models.models.models import *

from utils.UDatetime import UDatetime

from DAO.DataDAO import *

EST = pytz.timezone(TIME_ZONE)


class EventTierAllocationLoader:

    @classmethod
    def event_tier_loader(cls):
        EventTier.objects.all().delete()
        file_path = os.path.join(BASE_DIR, 'Models/loader/files/events tier and allocation.xlsx')
        records = pd.read_excel(file_path, 'tier')
        records = records.where((pd.notnull(records)), None)

        records = pd.melt(records, id_vars=['Order', 'Group', 'SubGroup', 'Product'],
                          var_name='tier',
                          value_name='price')
        records.dropna(subset=['price'], inplace=True)
        records.sort_values(['Order', 'tier'], inplace=True)

        for index, row in records.iterrows():
            if row['SubGroup'] == 'NA.':
                row['SubGroup'] = 'NA'
            # load records
            EventTier.objects.update_or_create(
                order=row['Order'],
                tier=row['tier'],
                defaults={
                    'group': row['Group'],
                    'subGroup': row['SubGroup'],
                    'product': row['Product'],
                    'price': round(float(row['price']), 2)
                }
            )

    @classmethod
    def event_allocation_loader(cls):
        EventAllocation.objects.all().delete()
        file_path = os.path.join(BASE_DIR, 'Models/loader/files/events tier and allocation.xlsx')
        records = pd.read_excel(file_path, 'allocation')
        records = records.where((pd.notnull(records)), None)
        records = pd.melt(records, id_vars=['Order', 'Group', 'SubGroup', 'Product', 'Sub Product'],
                          var_name='tier',
                          value_name='price')
        records.dropna(subset=['price'], inplace=True)
        records.sort_values(['Order', 'tier'], inplace=True)

        for index, row in records.iterrows():
            if row['SubGroup'] == 'NA.':
                row['SubGroup'] = 'NA'
            # load records
            EventAllocation.objects.update_or_create(
                order=row['Order'],
                tier=row['tier'],
                defaults={
                    'group': row['Group'],
                    'subGroup': row['SubGroup'],
                    'product': row['Product'],
                    'subProduct': row['Sub Product'],
                    'price': round(float(row['price']), 2)
                }
            )

    @classmethod
    def event_price_by_center_loader(cls):
        EventPriceByCenter.objects.all().delete()
        file_path = os.path.join(BASE_DIR, 'Models/loader/files/events tier and allocation.xlsx')
        records = pd.read_excel(file_path, 'By Center')
        records = records.where((pd.notnull(records)), None)
        records = pd.melt(records, id_vars=['Group', 'Center Number', 'Product', 'Order'],
                          var_name='duration',
                          value_name='price')
        records.dropna(subset=['price'], inplace=True)
        records.sort_values(['Group', 'Center Number', 'duration', 'Order'], inplace=True)
        records['price'] = records['price'].apply(lambda x: round(float(x), 2))

        for index, row in records.iterrows():
            center_obj = Centers.objects.get(center_id=row['Center Number'])

            # load records
            EventPriceByCenter.objects.update_or_create(
                group=row['Group'],
                center_id=center_obj,
                product=row['Product'],
                duration=row['duration'],
                defaults={
                    'price': row['price'],
                    'order': row['Order']
                }
            )

    @classmethod
    def event_promo_loader(cls):

        file_path = os.path.join(BASE_DIR, 'Models/loader/files/events tier and allocation.xlsx')
        records = pd.read_excel(file_path, 'promos')

        for index, row in records.iterrows():

            # load records
            EventPromo.objects.update_or_create(
                promo_code=row['Promo Code'],
                description=row['Description'],
            )

    @classmethod
    def event_center_tier_loader(cls):
        EventCenterTier.objects.all().delete()
        file_path = os.path.join(BASE_DIR, 'Models/loader/files/events tier and allocation.xlsx')
        records = pd.read_excel(file_path, 'Center tier')
        records = records.where((pd.notnull(records)), None)
        records = pd.melt(records, id_vars=['Center', 'Name'],
                          var_name='Product',
                          value_name='Tier')

        records.dropna(subset=['Tier'], inplace=True)
        records = records[records['Tier'] != 0 ]

        for index, row in records.iterrows():
            center_obj = Centers.objects.get(center_id=row['Center'])

            # load records
            EventCenterTier.objects.update_or_create(
                center_id=center_obj,
                product=row['Product'],
                defaults={
                    'tier': row['Tier']
                }
            )


if __name__ == "__main__":
    loader = input('Please give the loader type('
                   '1:load event tier;'
                   '2:load event allocation;'
                   '3:load event price by center;'
                   '4:load event promo;'
                   '5:load event center tier;'
                   '):')
    if int(loader) == 1:
        EventTierAllocationLoader.event_tier_loader()
    elif int(loader) == 2:
        EventTierAllocationLoader.event_allocation_loader()
    elif int(loader) == 3:
        EventTierAllocationLoader.event_price_by_center_loader()
    elif int(loader) == 4:
        EventTierAllocationLoader.event_promo_loader()
    elif int(loader) == 5:
        EventTierAllocationLoader.event_center_tier_loader()
