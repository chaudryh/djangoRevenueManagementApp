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

EST = pytz.timezone(TIME_ZONE)

DOW_map = {
           'Monday': 'mon',
           'Tuesday': 'tue',
           'Wednesday': 'wed',
           'Thursday': 'thu',
           'Friday': 'fri',
           'Saturday': 'sat',
           'Sunday': 'sun',
          }


class GEMSLoader:

    @classmethod
    def product_loader(cls):

        file_path = os.path.join(BASE_DIR, 'Models/loader/files/GEMS/All Products.xlsx')
        product_records = pd.read_excel(file_path)
        product_records = product_records.where((pd.notnull(product_records)), None)

        for index, row in product_records.iterrows():
            product_id = row['(Do Not Modify) Product'].upper()

            # load product
            Product.objects.update_or_create(
                product_id=product_id,
                defaults={
                    'product_name': row['Name'],
                    'readable_product_name': row['Name'],
                    'short_product_name': row['Name'],
                    'report_type': 'Event',
                    'always_opt_in': 'in',
                    'status': row['Status']
                }
            )

    @classmethod
    def product_base_loader(cls):

        file_path = os.path.join(BASE_DIR, 'Models/loader/files/GEMS/GemsActivePackageBaseTiers.xlsx')
        records = pd.read_excel(file_path)
        records = records.where((pd.notnull(records)), None)
        # records = records[records['ProductCategory'].isin(['PKG - Bowling', 'PKG - Adults', 'PKG - Lanes'])]

        for index, row in records.iterrows():
            price = row['BasePrice']
            price = round(float(price), 2) if price else None
            # load records
            product_obj, exist = ProductBase.objects.update_or_create(
                product_base_id=row['ProductPackageID'],
                defaults={
                    'product_base_name': row['ProductPackageBaseName'],
                    'price': price,
                    'currency': row['Currency'],
                    'package': row['Package'],
                    'pricing_tier': row['PricingTier'],
                    'product_name': row['ProductName'],
                    'product_category': row['ProductCategory'],
                    'hide_from_online_customers': row['HideFromOnlineCustomers'],
                    'status': row['ProductBaseStatus'],
                }
            )

    @classmethod
    def modifier_loader(cls):
        file_path = os.path.join(BASE_DIR, 'Models/loader/files/GEMS/Active Product Modifier Logic.xlsx')
        records = pd.read_excel(file_path)
        records = records.where((pd.notnull(records)), None)
        records = records[pd.notnull(records['Day of the Week'])]

        for index, row in records.iterrows():
            modifier_id = row['(Do Not Modify) Product Modifier Logic'].upper()
            price = row['Price Modifier']
            price = round(float(price), 2) if price else None
            price_percent = row['Price Modifier %']
            price_percent = round(float(price_percent), 2) if price_percent else None

            start_hour = row['Start Time Hour']
            start_hour = int(start_hour) if start_hour or start_hour == 0 else None
            start_min = row['Start Time Minute']
            start_min = int(start_min) if start_min or start_min == 0 else None
            end_hour = row['End Time Hour']
            end_hour = int(end_hour) if end_hour or end_hour == 0 else None
            end_min = row['End Time Minute']
            end_min = int(end_min) if end_min or end_min == 0 else None

            dow = row['Day of the Week']
            dow = DOW_map[dow] if dow else None

            # load records
            ProductModifier.objects.update_or_create(
                modifier_id=modifier_id,
                defaults={
                    'modifier_name': row['Name'],
                    'price': price,
                    'price_percent': price_percent,
                    'product_base_name': row['Pricing Package Product'],
                    'dow': dow,
                    'start_hour': start_hour,
                    'start_min': start_min,
                    'end_hour': end_hour,
                    'end_min': end_min,
                    'start_event_date': row['Start Date Event'],
                    'end_event_date': row['End Event Date'],
                    'start_day_of_month': row['Start Day of Month'],
                    'end_day_of_month': row['End Day of Month'],
                    'start_month': row['Start Month'],
                    'end_month': row['End Month'],
                    'status': row['Status'],
                }
            )


if __name__ == "__main__":
    loader = input('Please give the loader type('
                   '1:load GEMS product; '
                   '2:load GEMS product base; '
                   '3:init GEMS modifier; '
                   '):')
    if int(loader) == 1:
        GEMSLoader.product_loader()
    elif int(loader) == 2:
        GEMSLoader.product_base_loader()
    elif int(loader) == 3:
        GEMSLoader.modifier_loader()