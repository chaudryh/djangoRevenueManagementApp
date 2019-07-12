#To add new products to the menu, create an excel sheet with only the new products and run it using the second function.
# To create an entirely different menu and remove the old one, create and excel sheet with all the new menu items
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
from django.db.models import Q

from RM.Centers.models.models import Centers
from Food.FoodByCenter.models.models import *

EST = pytz.timezone(TIME_ZONE)


class FoodLoader:
#This function removes all old records and adds new ones from file
    @classmethod
    def food_loader(cls):

        file_path = os.path.join(BASE_DIR, 'Food/FoodByCenter/loader/files/FoodByCenter.xlsx')
        center_records = pd.read_excel(file_path, 'centers')
        food_records = pd.read_excel(file_path, 'food')

        center_records = center_records.where((pd.notnull(center_records)), None)
        food_records = food_records.where((pd.notnull(food_records)), None)

        # Create menus
        menus = food_records['Menu'].unique()
        for menu in menus:
            Menu.objects.update_or_create(menu_name=menu)

        # Create Food
        for index, row in food_records.iterrows():
            product_num = row['Product Num']
            product_name = row['Food'].strip()
            Product.objects.get_or_create(product_id=product_num,
                                          defaults={
                                              'product_name': product_name,
                                              'product_num': product_num,
                                              'readable_product_name': product_name,
                                              'short_product_name': product_name,
                                          })

        # Strip center food menu column
        # centers = Centers.objects.all()
        # for center in centers:
        #     if center.food_menu:
        #         center.food_menu = center.food_menu.strip()
        #         center.save()

        center_records = center_records[(center_records['Food_tier'].notnull()) &
                                        (center_records['Food_menu'].notnull())
                                        ]

        FoodPrice.objects.all().delete()
        for index, row in center_records.iterrows():

            center_id = row['Center_id']
            food_menu = row['Food_menu']
            food_tier = row['Food_tier']

            center = Centers.objects.get(center_id=center_id)
            food_menu = Menu.objects.get(menu_name=food_menu)

            foods = food_records[
                (food_records['Menu'] == food_menu.menu_name) &
                (food_records[food_tier].notnull())
                ]

            if foods.empty:
                continue

            for index_food, row_food in foods.iterrows():
                product_num = row_food['Product Num']
                category = row_food['Category']
                price = round(row_food[food_tier], 2)
                # start = row_food['Start']
                # end = row_food['End']

                product = Product.objects.get(product_id=product_num)
                # try:
                FoodPrice.objects.create(product=product,
                                         center_id=center,
                                         menu=food_menu,
                                         category=category,
                                         price=price,
                                         # start=start,
                                         # end=end
                                         )
                # except Exception as e:
                #     continue

            # print(foods)
            #
            # print(center_id, food_menu, food_tier)

        # menu_list = food_records['Menu'].unique()
        # for menu in menu_list:
        #     Menu.objects.update_or_create(
        #         name=menu,
        #     )
        #
        # food_records = pd.melt(food_records, id_vars=['Product Id',
        #                                               'Menu',
        #                                               'Sell Type',
        #                                               'Category',
        #                                               'Product Description',
        #                                               'Prod num',
        #                                               'Start',
        #                                               'End',
        #                                               'Status',
        #                                               ],
        #                        var_name='tier')
        # food_records = food_records[food_records['value'].notnull()]
        # for index, row in food_records.iterrows():
        #     start = row['Start']
        #     end = row['End']
        #
        #     product_num = row['Prod num']
        #     if product_num:
        #         product_num = str(int(product_num))
        #     else:
        #         product_num = None
        #
        #     # load food product
        #     product_obj, exist = Product.objects.update_or_create(
        #         product_id=row['Product Id'],
        #         defaults={
        #             'product_name': row['Product Description'],
        #             'product_num': product_num,
        #             'readable_product_name': row['Product Description'],
        #             'short_product_name': row['Product Description'],
        #             'status': row['Status']
        #         }
        #     )
        #
        #     # load product schedule
        #     # if not isinstance(start, pd.tslib.NaTType) or not isinstance(end, pd.tslib.NaTType):
        #     #     ProductSchedule.objects.update_or_create(
        #     #         product_id=product_obj,
        #     #         defaults={
        #     #             'start': row['Start'],
        #     #             'end': row['End'],
        #     #             'status': 'active',
        #     #             'product_name': product_obj.product_name,
        #     #             'action_time': UDatetime.now_local()
        #     #         }
        #     #     )
        #
        #     menu = Menu.objects.get(name=row['Menu'])
        #     price = round(float(row['value']), 2)
        #     FoodMenuTable.objects.update_or_create(
        #         product=product_obj,
        #         menu=menu,
        #         tier=row['tier'],
        #         category=row['Category'],
        #         defaults={
        #             'price': price,
        #             'status': 'active'
        #         }
        #     )


    # @classmethod
    # def menu_tier_load_processor(cls):
    #
    #     menu_objs = Menu.objects.all()
    #
    #     for menu in menu_objs:
    #         tier_list = FoodMenuTable.objects \
    #             .filter(menu=menu) \
    #             .values_list('tier', flat=True) \
    #             .distinct()
    #
    #         if tier_list.exists():
    #             for tier in tier_list:
    #                 MenuTier.objects.update_or_create(
    #                     menu=menu,
    #                     tier=tier,
    #                     defaults={
    #                         'status': 'active'
    #                     }
    #                 )
    #
    # @classmethod
    # def clean_product_ids(cls):
    #     foodmenu = FoodMenuTable.objects.filter(status='active')
    #     foodmenu_records = pd.DataFrame.from_records(foodmenu.values('id',
    #                                                                  'product',
    #                                                                  'product__product_num',
    #                                                                  ))
    @classmethod
    def food_new_loader(cls):

        file_path = os.path.join(BASE_DIR, 'Food/FoodByCenter/loader/files/FoodByCenter New Products.xlsx')
        center_records = pd.read_excel(file_path, 'centers')
        food_records = pd.read_excel(file_path, 'food')

        center_records = center_records.where((pd.notnull(center_records)), None)
        food_records = food_records.where((pd.notnull(food_records)), None)

        # Create menus
        menus = food_records['Menu'].unique()
        for menu in menus:
            Menu.objects.update_or_create(menu_name=menu)

        # Create Food
        for index, row in food_records.iterrows():
            product_num = row['Product Num']
            product_name = row['Food'].strip()
            Product.objects.get_or_create(product_id=product_num,
                                          defaults={
                                              'product_name': product_name,
                                              'product_num': product_num,
                                              'readable_product_name': product_name,
                                              'short_product_name': product_name,
                                          })

        center_records = center_records[(center_records['Food_tier'].notnull()) &
                                        (center_records['Food_menu'].notnull())
                                        ]

        for index, row in center_records.iterrows():

            center_id = row['Center_id']
            food_menu = row['Food_menu']
            food_tier = row['Food_tier']

            center = Centers.objects.get(center_id=center_id)
            food_menu = Menu.objects.get(menu_name=food_menu)

            foods = food_records[
                (food_records['Menu'] == food_menu.menu_name) &
                (food_records[food_tier].notnull())
                ]

            if foods.empty:
                continue

            for index_food, row_food in foods.iterrows():
                product_num = row_food['Product Num']
                category = row_food['Category']
                price = round(row_food[food_tier], 2)
                # start = row_food['Start']
                # end = row_food['End']

                product = Product.objects.get(product_id=product_num)
                # try:
                FoodPrice.objects.create(product=product,
                                         center_id=center,
                                         menu=food_menu,
                                         category=category,
                                         price=price,
                                         # start=start,
                                         # end=end
                                         )

    @classmethod
    def pivot_food(cls):

        file_path = os.path.join(BASE_DIR, 'Food/FoodByCenter/loader/files/Food.xlsx')
        records = pd.read_excel(file_path)

        records['food_prod_num'] = records[['food', 'product_num']].apply(lambda x: x['food'] + '---' + str(x['product_num']), axis=1)
        records.drop(['food', 'menu', 'category', 'product_num'], inplace=True, axis=1)
        records = pd.melt(records, id_vars=['food_prod_num'], var_name='center_id')

        records = pd.pivot_table(records,
                                 index=['center_id'],
                                 columns=['food_prod_num'],
                                 values=['value'],
                                 aggfunc='first'
                                 )

        records.columns = records.columns.droplevel(0)
        records.columns.name = None
        records.reset_index(inplace=True)
        records.to_excel('output.xlsx', index=False)

        # print(records)



if __name__ == "__main__":

    loader = input('Please give the loader type(1:food loader 2:food new loader):')
    if int(loader) == 1:
        FoodLoader.food_loader()
    elif int(loader) == 2:
        FoodLoader.food_new_loader()
