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

import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'bowlero_backend.settings'
django.setup()

from bowlero_backend.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse

from RM.Centers.models.models import *
from RM.Pricing.models.models import *
from RM.Food.models.models import *

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class FoodLoadProcessor:

    # @classmethod
    # def food_load_processor(cls):
    #
    #     file_path = os.path.join(BASE_DIR, 'RM/Centers/sample/config/food list.xlsx')
    #
    #     data = pd.read_excel(file_path)
    #
    #     for index, row in data.iterrows():
    #
    #         Food.objects\
    #             .update_or_create(
    #                 name=row['Food list'],
    #         )

    @classmethod
    def food_price_load_processor(cls):

        file_path_food = os.path.join(BASE_DIR, 'RM/Centers/sample/config/master food.xlsx')
        food_records = pd.read_excel(file_path_food)

        centers = Centers.objects.all()
        for center in centers:
            menu = center.food_menu
            if menu:
                food_tier = center.food_tier
                food_kiosk = center.food_kiosk

                food_tier = 'tier ' + food_tier
                if food_kiosk:
                    food_tier = 'kiosk ' + food_tier

                food_record = food_records[food_records['Menu'] == menu]
                menu = Menu.objects.get(name=center.food_menu)
                effective_datetime = UDatetime.now_local()

                for index, row in food_record.iterrows():
                    food = Food.objects.get(name=row['Product Description'])
                    price = round(float(row[food_tier]),2)
                    RetailFoodPrice.objects.update_or_create(
                        center_id=center,
                        food=food,
                        menu=menu,
                        defaults={
                            'price': price,
                            'status': 'active',
                            'effective_datetime': effective_datetime
                        }
                    )

    @classmethod
    def food_menu_master_load_processor(cls):

        file_path_food = os.path.join(BASE_DIR, 'RM/Centers/sample/config/master food.xlsx')
        food_records = pd.read_excel(file_path_food)
        food_records = food_records.where((pd.notnull(food_records)), None)

        effective_datetime = datetime.datetime(2018, 1, 1)

        menu_list = food_records['Menu'].unique()
        for menu in menu_list:
            Menu.objects.update_or_create(
                name=menu,
            )

        food_records = pd.melt(food_records, id_vars=['Product Id',
                                                      'Menu',
                                                      'Sell Type',
                                                      'Category',
                                                      'Product Description',
                                                      'Prod num',
                                                      'Start',
                                                      'End',
                                                      'Status',
                                                      ],
                               var_name='tier')
        food_records = food_records[food_records['value'].notnull()]

        for index, row in food_records.iterrows():
            start = row['Start']
            end = row['End']

            product_num = row['Prod num']
            if product_num:
                product_num = str(int(product_num))
            else:
                product_num = None

            # load food product
            product_obj, exist = Product.objects.update_or_create(
                product_id=row['Product Id'],
                defaults={
                    'product_name': row['Product Description'],
                    'product_num': product_num,
                    'readable_product_name': row['Product Description'],
                    'short_product_name': row['Product Description'],
                    'status': row['Status']
                }
            )

            # load product schedule
            if not isinstance(start, pd.tslib.NaTType) or not isinstance(end, pd.tslib.NaTType):
                ProductSchedule.objects.update_or_create(
                    product_id=product_obj,
                    defaults={
                        'start': row['Start'],
                        'end': row['End'],
                        'status': 'active',
                        'product_name': product_obj.product_name,
                        'action_time': UDatetime.now_local()
                    }
                )

            menu = Menu.objects.get(name=row['Menu'])
            price = round(float(row['value']), 2)
            FoodMenuTable.objects.update_or_create(
                product=product_obj,
                menu=menu,
                tier=row['tier'],
                category=row['Category'],
                defaults={
                    'price': price,
                    'status': 'active'
                }
            )

    @classmethod
    def menu_tier_load_processor(cls):

        menu_objs = Menu.objects.all()

        for menu in menu_objs:
            tier_list = FoodMenuTable.objects \
                .filter(menu=menu) \
                .values_list('tier', flat=True) \
                .distinct()

            if tier_list.exists():
                for tier in tier_list:
                    MenuTier.objects.update_or_create(
                        menu=menu,
                        tier=tier,
                        defaults={
                            'status': 'active'
                        }
                    )


if __name__ == "__main__":
    # FoodLoadProcessor.food_load_processor()
    # FoodLoadProcessor.food_price_load_processor()

    # loader = input('Please give the loader type(1:food menu price table, 2:menu_tier):')
    # if int(loader) == 1:
        FoodLoadProcessor.food_menu_master_load_processor()
    # elif int(loader) == 2:
    #     FoodLoadProcessor.menu_tier_load_processor()