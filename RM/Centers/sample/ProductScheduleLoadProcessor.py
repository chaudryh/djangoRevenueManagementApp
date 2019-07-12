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

        file_path = os.path.join(BASE_DIR, 'RM/Centers/sample/config/Product Schedule list.xlsx')
        product_schedule_records = pd.read_excel(file_path)
        product_schedule_records = product_schedule_records.where((pd.notnull(product_schedule_records)), None)

        for index, row in product_schedule_records.iterrows():
            product_obj = Product.objects.get(product_id=row['Product Id'])

            start_time = row['Start']
            if start_time:
                start = dt.combine(dt(1900, 1, 1), start_time)
            else:
                start = None

            end_time = row['End']
            if end_time:
                end = dt.combine(dt(1900, 1, 1), end_time)
            else:
                end = None

            ProductSchedule.objects.update_or_create(
                product_id=product_obj,
                DOW=row['DOW'],
                start=start,
                end=end,
                freq='Weekly',
                defaults={
                    'status': 'active',
                    'product_name': product_obj.product_name
                }
            )


if __name__ == "__main__":
    ProductLoadProcessor.product_load_processor()