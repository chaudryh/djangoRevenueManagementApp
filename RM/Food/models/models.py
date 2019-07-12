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


# class Food(models.Model):
#     # food_id = models.CharField(max_length=100, primary_key=True)
#     name = models.CharField(max_length=100, null=True, blank=True)
#     sell_type = models.CharField(default='retail', max_length=30, choices=sell_type_choice)


class Menu(models.Model):
    menu_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    sell_type = models.CharField(default='retail', max_length=30, choices=sell_type_choice)
    status = models.CharField(default='active', max_length=30, choices=status_choice)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


# class FoodMenu(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product', null=True, blank=True)
#     menu = models.ForeignKey(Menu, on_delete=models.CASCADE, db_column='menu', null=True, blank=True)


class MenuTier(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, db_column='menu', null=True, blank=True)
    tier = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(default='inactive', max_length=30, choices=status_choice)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


class FoodMenuTable(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product', null=True, blank=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, db_column='menu', null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    tier = models.CharField(max_length=100, null=True, blank=True)
    # effective_datetime = models.DateTimeField(default=timezone.now)
    status = models.CharField(default='inactive', max_length=30, choices=status_choice)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


# class RetailFoodPrice(models.Model):
#     price = models.FloatField()
#     unit_type = models.CharField(default='by_unit', max_length=30, choices=PricingChoice.unit_type)
#     effective_datetime = models.DateTimeField(default=timezone.now)
#     status = models.CharField(default='inactive', max_length=30, choices=status_choice)
#     center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
#                                   null=True, blank=True)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product',
#                                 null=True, blank=True)
#     menu = models.ForeignKey(Menu, on_delete=models.CASCADE, db_column='menu',
#                              null=True, blank=True)
#
#     # Tracking
#     action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
#                                     null=True, blank=True)
#     action_time = models.DateTimeField(default=timezone.now)
#     tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
#                                     null=True, blank=True)
#
#
# class EventFoodPrice(models.Model):
#     price = models.FloatField()
#     unit_type = models.CharField(default='by_unit', max_length=30, choices=PricingChoice.unit_type)
#     effective_datetime = models.DateTimeField(default=timezone.now)
#     status = models.CharField(default='inactive', max_length=30, choices=status_choice)
#     center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
#                                   null=True, blank=True)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product',
#                              null=True, blank=True)
#     menu = models.ForeignKey(Menu, on_delete=models.CASCADE, db_column='menu',
#                              null=True, blank=True)
#
#     # Tracking
#     action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
#                                     null=True, blank=True)
#     action_time = models.DateTimeField(default=timezone.now)
#     tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
#                                     null=True, blank=True)

