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

EST = pytz.timezone(TIME_ZONE)


class PriceTierLoadProcessor:

    @classmethod
    def price_tier_load_processor(cls):

        file_path = os.path.join(BASE_DIR, 'RM/Centers/sample/config/Pricing Tier Table.xlsx')

        data_xp_bowling = pd.read_excel(file_path, 'XP Bowling')
        data_xp_shoes = pd.read_excel(file_path, 'XP Shoes')
        data_trad_bowling = pd.read_excel(file_path, 'Traditional Bowling')
        data_trad_shoes = pd.read_excel(file_path, 'Traditional Shoes')

        cls.price_tier_load_detail_processor(data_xp_bowling, 'experiential', 'bowling')
        cls.price_tier_load_detail_processor(data_xp_shoes, 'experiential', 'shoe')
        cls.price_tier_load_detail_processor(data_trad_bowling, 'traditional', 'bowling')
        cls.price_tier_load_detail_processor(data_trad_shoes, 'traditional', 'shoe')

    @classmethod
    def price_tier_load_detail_processor(cls, data, center_type, product):

        data = pd.melt(data, id_vars=['Day', 'Time', 'Category', 'Order'], var_name='tier')

        # print(data)
        for index, row in data.iterrows():
            period_label = row['Category']
            if product == 'shoe':
                product_name = 'retail shoe'
            else:
                product_name = 'retail {center_type} {period_label} {product}' \
                    .format(center_type=center_type, period_label=period_label, product=product)
            product_obj = Product.objects.get(product_name=product_name)

            PricingTierTable.objects.update_or_create(
                DOW=row['Day'],
                time=row['Time'],
                period_label=row['Category'],
                tier=row['tier'],
                product_id=product_obj,
                product_name=product_obj.product_name,
                center_type=center_type,
                defaults={
                    'price': round(float(row['value']), 2),
                    'order': row['Order']
                }
            )

    @classmethod
    def price_tier_load_processor_new(cls):

        file_path = os.path.join(BASE_DIR, 'RM/Centers/sample/config/Pricing Tier Table.xlsx')

        data_xp_bowling = pd.read_excel(file_path, 'XP Bowling')
        data_xp_shoes = pd.read_excel(file_path, 'XP Shoes')
        data_trad_bowling = pd.read_excel(file_path, 'Traditional Bowling')
        data_trad_shoes = pd.read_excel(file_path, 'Traditional Shoes')
        cls.price_tier_load_detail_processor_new(data_xp_bowling, 'experiential', 'bowling')
        cls.price_tier_load_detail_processor_new(data_xp_shoes, 'experiential', 'shoe')
        cls.price_tier_load_detail_processor_new(data_trad_bowling, 'traditional', 'bowling')
        cls.price_tier_load_detail_processor_new(data_trad_shoes, 'traditional', 'shoe')

    @classmethod
    def price_tier_load_detail_processor_new(cls, data, center_type, product):
        data = pd.melt(data, id_vars=['Day', 'Time', 'Category', 'Order'], var_name='tier')

        for index, row in data.iterrows():
            period_label = row['Category']
            dow = row['Day']
            if product == 'shoe':
                product_id = '107'
            else:
                if period_label == 'non-prime':
                    product_id = '108'
                elif period_label == 'prime':
                    if dow in DOW_weekday:
                        product_id = '110'
                    elif dow in DOW_weekend:
                        product_id = '111'
                    else:
                        continue
                elif period_label == 'premium':
                    product_id = '113'
                else:
                    continue

            product_obj = Product.objects.get(product_id=product_id)

            PricingTierTable.objects.update_or_create(
                DOW=row['Day'],
                time=row['Time'],
                period_label=row['Category'],
                tier=row['tier'],
                product_id=product_obj,
                product_name=product_obj.product_name,
                center_type=center_type,
                defaults={
                    'price': round(float(row['value']), 2),
                    'order': row['Order']
                }
            )


if __name__ == "__main__":
    loader = input('Please give the loader type(1:load tier price old product, 2:load tier price new product):')
    if int(loader) == 1:
        PriceTierLoadProcessor.price_tier_load_processor()
    elif int(loader) == 2:
        PriceTierLoadProcessor.price_tier_load_processor_new()
