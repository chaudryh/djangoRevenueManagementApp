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
from Email.EmailNotice.models.models import *

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class EmailLoadProcessor:

    @classmethod
    def email_load_processor(cls):

        file_path = os.path.join(BASE_DIR, 'RM/Centers/sample/config/emails.xlsx')
        EmailNoticeType_records = pd.read_excel(file_path, 'EmailNoticeType')
        EmailNoticeGroup_records = pd.read_excel(file_path, 'EmailNoticeGroup')
        EmailNoticeGroupUser_records = pd.read_excel(file_path, 'EmailNoticeGroupUser')
        EmailNoticeReceiver_records = pd.read_excel(file_path, 'EmailNoticeReceiver')

        for index, row in EmailNoticeType_records.iterrows():
            EmailNoticeType.objects.update_or_create(
                notice_type_id=row['notice_type_id'],
                defaults={
                    'notice_name': row['notice_name'],
                }
            )

        for index, row in EmailNoticeGroup_records.iterrows():
            EmailNoticeGroup.objects.update_or_create(
                group_id=row['group_id'],
                defaults={
                    'group_name': row['group_name'],
                }
            )

        for index, row in EmailNoticeGroupUser_records.iterrows():
            group_obj = EmailNoticeGroup.objects.get(group_id=row['group_id'])
            username = User.objects.get(username=row['username'])

            EmailNoticeGroupUser.objects.update_or_create(
                group_id=group_obj,
                username=username,
            )

        for index, row in EmailNoticeReceiver_records.iterrows():
            notice_type_obj = EmailNoticeType.objects.get(notice_type_id=row['notice_type_id'])
            if not pd.isna(row['group_id']):
                group_obj = EmailNoticeGroup.objects.get(group_id=str(int(row['group_id'])))
                EmailNoticeReceiver.objects.update_or_create(
                    receiver_id=row['receiver_id'],
                    defaults={
                        'notice_type_id': notice_type_obj,
                        'group_id': group_obj,
                    }
                )
            else:
                username = User.objects.get(username=row['username'])
                EmailNoticeReceiver.objects.update_or_create(
                    receiver_id=row['receiver_id'],
                    defaults={
                        'notice_type_id': notice_type_obj,
                        'username': username,
                    }
                )

    @classmethod
    def email_default_load(cls):
        active_users = User.objects.filter(is_active=True, is_staff=True)

        group_obj, exist_group = EmailNoticeGroup.objects.update_or_create(
            group_name='All active staff users',
        )

        for active_user in active_users:
            EmailNoticeGroupUser.objects.update_or_create(
                group_id=group_obj,
                username=active_user,
            )

        notice_type_obj = EmailNoticeType.objects.get(notice_type_id=1)
        EmailNoticeReceiver.objects.update_or_create(
            notice_type_id=notice_type_obj,
            group_id=group_obj,
        )


if __name__ == "__main__":
    EmailLoadProcessor.email_load_processor()
    # EmailLoadProcessor.email_default_load()