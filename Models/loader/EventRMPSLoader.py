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


class EventRMPSLoader:

    @classmethod
    def event_RMPS_loader(cls):
        file_path = os.path.join(BASE_DIR, 'Models/loader/files/RMPS Combined text.xlsx')
        records = pd.read_excel(file_path, 'RMPS', skiprows=2)
        columns = pd.read_excel(file_path, 'columns')
        #print(records)

        records = pd.melt(records,
                          id_vars=['Center Id'],
                          var_name='attribute',
                          value_name='value')
        #print(records)
        #records['attribute'] = records['attribute'].replace('\n', '', regex=True)
        #print(records['attribute'])
        #print(columns['attribute'])
        #print(columns['order'])
        #print(records.to_string)
        # centers = records[records.columns[0:1]]  # first five columns of excel sheet
        # print(centers)
        # records.drop(records.columns[[0]], axis=1, inplace=True)

        #columns['attribute'] = columns['attribute'].replace('\n', '', regex=True)
        records = records.join(columns.set_index(['attribute']), on=['attribute'], how='left')
        #print(records)
        #print(columns.set_index(['attribute']))
        # columns.set_index(['order'])
        # records=records.join(columns, on=['order'], how='left')
        # #records=records.join(x, on=['attribute'], how='left')

        #records = pd.concat([records, x], axis=1)

        #records = records.merge(columns, how='left', left_on = 'attribute', right_on='attribute')

        records = records.where((pd.notnull(records)), None)
        #data2 = pd.concat([centers, records], axis=1)

        print(records)

        RMPS.objects.all().delete()
        for index, row in records.iterrows():
            value = row['value']
            if row['unit'] == 'dollar':
                value = str(int(value)) if value and value % 1 == 0 else value
            # if row['attribute'] == 'HOLIDAY PARTIES\n 2 Hours Bowling incl Shoe Rental---Tier':
            #     row['attribute'] = row['attribute'].replace('\n', '', regex=True)
            center_obj = Centers.objects.get(center_id=row['Center Id'])
            RMPS.objects.create(center_id=center_obj,
                                attribute=row['attribute'].rstrip(),
                                value=value,
                                order=row['order'],
                                unit=row['unit'],
                                )

    @classmethod
    def event_RMPS_columns_update(cls):
        mapping = {
            # 'NYE Ball Drop (9pm-1am)---Tier': 'NYE Ball Drop---Tier',
            # 'NYE Ball Drop (9pm-1am)---Price': 'NYE Ball Drop---Price',
            # 'Teen Packages  *arcade---Tier': 'Teen Packages *Arcade---Tier',
            # 'Teen Packages  *arcade---All Star': 'Teen Packages *Arcade---All Star',
            # 'Teen Packages  *arcade---Varsity': 'Teen Packages *Arcade---Varsity',
            # 'Teen Parent Plate * Arcade---Tier': 'Teen Parent Plate---Tier',
            # 'Teen Parent Plate * Arcade---All Star': 'Teen Parent Plate---All Star',
            # 'Teen Parent Plate * Arcade---Varsity': 'Teen Parent Plate---Varsity',
            # 'KIDS BIRTHDAY PARTY PACKAGES  *Arcade Card---Tier': 'Kids Birthday *Arcade---Tier',
            # 'KIDS BIRTHDAY PARTY PACKAGES  *Arcade Card---Legend': 'Kids Birthday *Arcade---Legend',
            # 'KIDS BIRTHDAY PARTY PACKAGES  *Arcade Card---Superstar': 'Kids Birthday *Arcade---Superstar',
            # 'KIDS BIRTHDAY PARTY PACKAGES  *Arcade Card---Celebrity': 'Kids Birthday *Arcade---Celebrity',
            # 'KIDS BIRTHDAY PARTY PACKAGES  *Arcade Card---A-List': 'Kids Birthday *Arcade---A-List',
            # 'KIDS BIRTHDAY PARTY PACKAGES  *Arcade Card---Paparazzi': 'Kids Birthday *Arcade---Paparazzi',
            # 'Kids Parent Plate (Food Portion)---Tier': 'Kids Parent Plate---Tier',
            # 'Kids Parent Plate (Food Portion)---Legend Parent Plate': 'Kids Parent Plate---Legend Parent Plate',
            # 'Kids Parent Plate (Food Portion)---Superstar Parent Plate': 'Kids Parent Plate---Superstar Parent Plate',
            # 'Kids Parent Plate (Food Portion)---Celebrity Parent Plate': 'Kids Parent Plate---Celebrity Parent Plate',
            # 'Kids Parent Plate (Food Portion)---A-List Parent Plate': 'Kids Parent Plate---A-List Parent Plate',
            # 'Kids - Pampered Parent---Tier': 'Kids Pampered Parent---Tier',
            # 'Kids - Pampered Parent---Legend Pampered Parent': 'Kids Pampered Parent---Legend Pampered Parent',
            # 'Kids - Pampered Parent---Superstar Pampered Parent': 'Kids Pampered Parent---Superstar Pampered Parent',
            # 'Kids - Pampered Parent---Celebrity Pampered Parent': 'Kids Pampered Parent---Celebrity Pampered Parent',
            # 'Kids - Pampered Parent---A-List Pampered Parent': 'Kids Pampered Parent---A-List Pampered Parent',
            # 'Kids - Pampered Parent---Paparazzi Pampered Parent': 'Kids Pampered Parent---Paparazzi Pampered Parent',
            # 'Daycare/Camp---Camp Tier': 'Daycare/Camp *Arcade---Camp Tier',
            # 'Daycare/Camp---Daycare/ Camp 1.5 hr': 'Daycare/Camp *Arcade---Daycare/ Camp 1.5 hr',
            # 'Daycare/Camp---Daycare/ Camp 1.5 hr w Food': 'Daycare/Camp *Arcade---Daycare/ Camp 1.5 hr w Food',
            'Mega/Gamerz---Gamerz Pampered Parent Tier': 'Mega/Gamerz Pampered Parent---Gamerz Pampered Parent Tier',
            'Mega/Gamerz---Gamerz Pampered Parent': 'Mega/Gamerz Pampered Parent---Gamerz Pampered Parent',
            'Mega/Gamerz---Mega-Gamerz Pampered Parent': 'Mega/Gamerz Pampered Parent---Mega-Gamerz Pampered Parent',
        }
        #

        for k, v in mapping.items():
            RMPS.objects.filter(attribute=k).update(attribute=v)

    @classmethod
    def event_RMPS_new_products(cls):
        file_path = os.path.join(BASE_DIR, 'Models/loader/files/Mega prods.xlsx')
        records = pd.read_excel(file_path, 'RMPS', skiprows=2)
        columns = pd.read_excel(file_path, 'columns')
        records = pd.melt(records,
                          id_vars=['Center Id'],
                          var_name='attribute',
                          value_name='value')
        records = records.join(columns.set_index(['attribute']), on=['attribute'], how='left')
        records = records.where((pd.notnull(records)), None)
        print(records)
        #records.dropna(subset=['value'], inplace=True)

        for index, row in records.iterrows():
            value = row['value']
            if row['unit'] == 'dollar':
                value = str(int(value)) if value and value % 1 == 0 else value

            center_obj = Centers.objects.get(center_id=row['Center Id'])
            RMPS.objects.create(center_id=center_obj,
                                attribute=row['attribute'].rstrip(),
                                value=value,
                                order=row['order'],
                                unit=row['unit'],
                                )

    @classmethod
    def event_RMPS_columns_order_update(cls):
        file_path = os.path.join(BASE_DIR, 'Models/loader/files/update order.xlsx')
        columns = pd.read_excel(file_path, 'columns')

        for index, row in columns.iterrows():
            RMPS.objects \
                .filter(attribute=row['attribute']) \
                .update(order=row['order'])


if __name__ == "__main__":
    loader = input('Please give the loader type('
                   '1:load event RMPS;'
                   '2:update event RMPS columns;'
                   '3:add new products;'
                   '4:update columns order'
                   '):')
    if int(loader) == 1:
        EventRMPSLoader.event_RMPS_loader()
    elif int(loader) == 2:
        EventRMPSLoader.event_RMPS_columns_update()
    elif int(loader) == 3:
        EventRMPSLoader.event_RMPS_new_products()
    elif int(loader) == 4:
        EventRMPSLoader.event_RMPS_columns_order_update()
