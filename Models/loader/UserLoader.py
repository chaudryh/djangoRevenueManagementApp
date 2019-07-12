import os
import sys
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt
import pytz
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'bowlero_backend.settings'
django.setup()

from bowlero_backend.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from accounts.models import User

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)

UNUSABLE_PASSWORD_PREFIX = '!'  # This will never be a valid encoded hash
UNUSABLE_PASSWORD_SUFFIX_LENGTH = 40  # number of random chars to add after UNUSABLE_PASSWORD_PREFIX


class UserLoader:

    @classmethod
    def createUsers(cls):

        file_path = os.path.join(BASE_DIR, 'Models/loader/files/web accounts.xlsx')

        data = pd.read_excel(file_path)
        data = data.where((pd.notnull(data)), None)
        data = data[data['sync'] == 'no']

        for index, row in data.iterrows():
            account = row['account']
            password = row['password']
            firstName = row['first name']
            lastName = row['last name']
            user = User.objects.filter(username=account)
            if not user.exists():
                user = User.objects.create_user(username=account,
                                                email=account,
                                                password=password,
                                                first_name=firstName,
                                                last_name=lastName,
                                                is_staff=True
                                                )
            else:
                user = User.objects \
                    .filter(username=account) \
                    .update(
                        email=account,
                        password=make_password(password),
                        first_name=firstName,
                        last_name=lastName,
                        is_staff=True
                    )


if __name__ == '__main__':
    UserLoader.createUsers()

