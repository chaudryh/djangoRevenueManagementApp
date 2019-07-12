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
from django.db.models import Q

from RM.Centers.models.models import *
from RM.Pricing.models.models import *
from RM.Food.models.models import *

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class BundleLoadProcessor:

    @classmethod
    def bundle_load_processor(cls):

        file_path = os.path.join(BASE_DIR, 'RM/Centers/sample/config/bundle.xlsx')
        bundle_records = pd.read_excel(file_path)

        for index, row in bundle_records.iterrows():
            bundle_obj, exist = Bundle.objects.update_or_create(
                bundle_id=row['bundle id'],
                defaults={
                    'bundle_name': row['bundle name'],
                }
            )

            product_objs = Product.objects.filter(Q(product_num=row['product id']) |
                                                  Q(product_id=row['product id']))
            if product_objs.exists():
                product_obj = product_objs[0]
            else:
                product_obj, exist = Product.objects.update_or_create(
                    product_id=row['product id'],
                    defaults={
                        'product_name': row['product name'],
                        'readable_product_name': row['product name'],
                        'short_product_name': row['product name'],
                        'product_num': row['product id'],
                        'report_type': 'Retail Promos',
                    }
                )

            BundleProduct.objects.update_or_create(
                bundle_id=bundle_obj,
                product_id=product_obj
            )


if __name__ == "__main__":
    BundleLoadProcessor.bundle_load_processor()