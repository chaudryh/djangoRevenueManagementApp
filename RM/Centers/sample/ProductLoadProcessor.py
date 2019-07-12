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

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class ProductLoadProcessor:

    @classmethod
    def product_load_processor(cls):

        file_path = os.path.join(BASE_DIR, 'RM/Centers/sample/config/Product list.xlsx')
        product_records = pd.read_excel(file_path)

        for index, row in product_records.iterrows():
            if row['Product Num'] and not pd.isna(row['Product Num']):
                product_num = str(int(row['Product Num']))
            else:
                product_num = None
            # load food product
            product_obj, exist = Product.objects.update_or_create(
                product_id=row['Product Id'],
                defaults={
                    'product_name': row['Product name'],
                    'readable_product_name': row['Readable product name'],
                    'short_product_name': row['Short porduct name'],
                    'product_num': product_num,
                    'report_type': row['Report type'],
                    'order': row['Order']
                }
            )


if __name__ == "__main__":
    ProductLoadProcessor.product_load_processor()