from django.db import models
from django.utils import timezone
from accounts.models import User

import pytz
from dateutil import tz
import datetime

from configurations.config_models.models_choice import *
from Audit.models.models import *
from RM.Centers.models.models import *
from RM.Pricing.models.models import *
# Create your models here.


# class AlcoholCategory(models.Model):
#     category_id = models.AutoField(primary_key=True)
#     category = models.CharField(max_length=100, null=True, blank=True)
#     level = models.CharField(max_length=100, null=True, blank=True)
#     price_type = models.CharField(max_length=100, null=True, blank=True)
#
#     # Tracking
#     action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
#                                     null=True, blank=True)
#     action_time = models.DateTimeField(default=timezone.now)
#     tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
#                                     null=True, blank=True)
#
#
# class Alcohol(models.Model):
#     product_id = models.ForeignKey(Product, on_delete=models.CASCADE, to_field='product_id', db_column='product_id')
#     category_id = models.ForeignKey(AlcoholCategory, on_delete=models.CASCADE, to_field='category_id',
#                                     db_column='category_id')
#     traditional_menu = models.BooleanField(default=True)
#     premium_menu = models.BooleanField(default=True)
#     start = models.DateTimeField(null=True, blank=True)
#     end = models.DateTimeField(null=True, blank=True)
#
#     # Tracking
#     action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
#                                     null=True, blank=True)
#     action_time = models.DateTimeField(default=timezone.now)
#     tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
#                                     null=True, blank=True)
#
#
# class AlcoholTier(models.Model):
#     category_id = models.ForeignKey(AlcoholCategory, on_delete=models.CASCADE, to_field='category_id',
#                                     db_column='category_id')
#     tier = models.CharField(max_length=100, null=True, blank=True)
#     price = models.FloatField(null=True, blank=True)
#     start = models.DateTimeField(null=True, blank=True)
#     end = models.DateTimeField(null=True, blank=True)
#
#     # Tracking
#     action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
#                                     null=True, blank=True)
#     action_time = models.DateTimeField(default=timezone.now)
#     tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
#                                     null=True, blank=True)
