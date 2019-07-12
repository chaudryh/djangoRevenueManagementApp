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
from RM.Food.models.models import *
from Alcohol.Alcohol.models.models import *

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class AlcoholLoadProcessor:

    @classmethod
    def alcohol_product_load_processor(cls):

        file_path = os.path.join(BASE_DIR, 'RM/Centers/sample/config/Alcohol.xlsx')
        records = pd.read_excel(file_path, 'products')
        for index, row in records.iterrows():

            # load food product
            product_obj, exist = Product.objects.update_or_create(
                product_id=row['Product Num'],
                defaults={
                    'product_name': row['Product Name'],
                    'readable_product_name': row['Product Name'],
                    'short_product_name': row['Product Name'],
                    'product_num': row['Product Num'],
                }
            )

    @classmethod
    def alcohol_tier_load_processor(cls):

        file_path = os.path.join(BASE_DIR, 'RM/Centers/sample/config/Alcohol.xlsx')
        records = pd.read_excel(file_path, 'tiers')

        for index1, row1 in records.iterrows():

            # load food product
            AlcoholCategory.objects.update_or_create(
                category=row1['category'],
                level=row1['level'],
            )

        records = pd.melt(records, id_vars=['price_type', 'category', 'level'], var_name='tier')
        for index2, row2 in records.iterrows():
            category_id = AlcoholCategory.objects.get(category=row2['category'],
                                                      level=row2['level']
                                                      )
            AlcoholTier.objects.update_or_create(
                category_id=category_id,
                tier=row2['tier'],
                price_type=row2['price_type'],
                defaults={
                    'price': row2['value'],
                    'category': row2['category'],
                    'level': row2['level']
                }
            )

    @classmethod
    def alcohol_alcohol_load_processor(cls):

        file_path = os.path.join(BASE_DIR, 'RM/Centers/sample/config/Alcohol.xlsx')
        records = pd.read_excel(file_path, 'Alcohol')
        records = records[~(records['clear'] == 'no')]
        records['Product Num'] = records['Product Num'].astype(int).astype(str)
        records = records.where((pd.notna(records)), None)

        for index, row in records.iterrows():
            product_id = Product.objects.get(product_id=row['Product Num'])
            try:
                category_id = AlcoholCategory.objects.get(level=row['level'], category=row['Tier Category'])
            except:
                category_id = None

            if row['trad'] == 'yes':
                trad = True
            else:
                trad = False

            if row['prem'] == 'yes':
                prem = True
            else:
                prem = False

            # load food product
            Alcohol.objects.update_or_create(
                product_id=product_id,
                category_id=category_id,
                defaults={
                    'traditional_menu': trad,
                    'premium_menu': prem,
                    'category': row['Tier Category'],
                    'level': row['level']
                }
            )

    @classmethod
    def loader(cls):
        cls.alcohol_product_load_processor()
        cls.alcohol_tier_load_processor()
        cls.alcohol_alcohol_load_processor()

    @classmethod
    def beer_processer(cls):
        file_path = os.path.join(BASE_DIR, 'RM/Centers/sample/config/beer.xlsx')
        records = pd.read_excel(file_path, 'beer')
        records = pd.melt(records, id_vars=[], var_name='category')
        records = records[~pd.isna(records['value'])]
        records.to_csv('bear_clean.csv')

        print(records)


if __name__ == "__main__":
    AlcoholLoadProcessor.loader()
    # AlcoholLoadProcessor.beer_processer()