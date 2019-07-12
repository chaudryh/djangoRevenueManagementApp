import os
import sys
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt
import pytz
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'bowlero_backend.settings'
django.setup()

from bowlero_backend.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse
from django.db.models import Q, Count, Min, Max, Sum, Avg

from RM.Centers.models.models import *
from RM.Food.models.models import *
from Models.models.models import *

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class RetailPromosLoader:

    old_start = dt(2018, 1, 1)
    new_start = dt(2018, 6, 18)

    @classmethod
    def retail_promos_loader(cls):

        file_path = os.path.join(BASE_DIR, 'Models/loader/files/retail promos.xlsx')

        data = pd.read_excel(file_path)
        data = data.where((pd.notnull(data)), None)
        data = pd.melt(data, id_vars=['Center'], var_name='product_id', value_name='price')
        data['product_id'], data['type'] = data['product_id'].str.split('-').str

        data_old = data[data['type'] == 'old']
        data_new = data[data['type'] == 'new']

        # Load into database
        for index, row in data_old.iterrows():
            center_obj = Centers.objects.get(center_id=row['Center'])
            product_obj = Product.objects.get(Q(product_id=row['product_id']) | Q(product_num=row['product_id']))

            price = row['price']
            if price:
                price = round(price, 2)
            else:
                continue

            ProductPriceChange.objects \
                .update_or_create(
                start=cls.old_start,
                end=None,
                center_id=center_obj,
                product_id=product_obj,
                defaults={
                    'price': round(row['price'], 2),
                    'perpetual': True,
                    'product_name': product_obj.product_name,
                }
            )

        for index, row in data_new.iterrows():
            center_obj = Centers.objects.get(center_id=row['Center'])
            product_obj = Product.objects.get(Q(product_id=row['product_id']) | Q(product_num=row['product_id']))

            price = row['price']
            if price:
                price = round(price, 2)
                ProductPriceChange.objects \
                    .update_or_create(
                        start=cls.new_start,
                        end=None,
                        center_id=center_obj,
                        product_id=product_obj,
                        defaults={
                            'price': round(row['price'], 2),
                            'perpetual': True,
                            'product_name': product_obj.product_name,
                        }
                    )
                ProductOpt.objects.update_or_create(
                    product_id=product_obj,
                    center_id=center_obj,
                    start=cls.new_start,
                    end=None,
                    defaults={
                        'opt': 'In',
                    }
                )
            else:
                ProductOpt.objects.update_or_create(
                    product_id=product_obj,
                    center_id=center_obj,
                    start=cls.new_start,
                    end=None,
                    defaults={
                        'opt': 'Out',
                    }
                )

    # After Party Friday Loader for 2018.9.4
    @classmethod
    def after_party_friday_loader(cls):

        start = dt(2018, 9, 4)
        after_party_friday_product_ids = ['2146481686', '2146532909', '2146507303', '2146481687']

        file_path = os.path.join(BASE_DIR, 'Models/loader/files/retail promos.xlsx')

        data = pd.read_excel(file_path, 'AfterPartyFridays20180904')
        data = data.where((pd.notnull(data)), None)
        data['Product Num'] = data['Product Num'].apply(lambda x: str(int(x)) if x else x)

        # Load into database
        for index, row in data.iterrows():
            center_obj = Centers.objects.get(center_id=row['Center'])
            price = row['Price']
            if price:
                product_id = row['Product Num']
                product_obj = Product.objects.get(product_id=product_id)
                price = round(price, 2)
                ProductPriceChange.objects \
                    .update_or_create(
                        start=start,
                        end=None,
                        center_id=center_obj,
                        product_id=product_obj,
                        defaults={
                            'price': price,
                            'perpetual': True,
                            'product_name': product_obj.product_name,
                        }
                    )
                ProductOpt.objects.update_or_create(
                    product_id=product_obj,
                    center_id=center_obj,
                    start=start,
                    end=None,
                    defaults={
                        'opt': 'In',
                    }
                )

                products_optout = [x for x in after_party_friday_product_ids if x != product_id]
            else:
                products_optout = after_party_friday_product_ids

            for product_optout in products_optout:
                product_obj = Product.objects.get(product_id=product_optout)
                ProductOpt.objects.update_or_create(
                    product_id=product_obj,
                    center_id=center_obj,
                    start=start,
                    end=None,
                    defaults={
                        'opt': 'Out',
                    }
                )


if __name__ == '__main__':
    # RetailPromosLoader.retail_promos_loader()
    RetailPromosLoader.after_party_friday_loader()

