from django.db import models
from django.utils import timezone
from accounts.models import User

from configurations.config_models.models_choice import *
from Audit.models.models import Tracking
from RM.Centers.models.models import Centers
from RM.Pricing.models.models import Product
# Create your models here.


# class Food(models.Model):
#
#     product_id = models.CharField(max_length=100, primary_key=True)
#     product_name = models.CharField(max_length=100, null=True, blank=True)
#     readable_product_name = models.CharField(max_length=100, null=True, blank=True)
#     short_product_name = models.CharField(max_length=100, null=True, blank=True)
#     report_type = models.CharField(max_length=100, null=True, blank=True)
#     order = models.IntegerField(null=True, blank=True)
#     status = models.CharField(default='active', max_length=30, choices=status_choice)
#
#     # Tracking
#     action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
#                                     null=True, blank=True)
#     action_time = models.DateTimeField(default=timezone.now)
#     tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
#                                     null=True, blank=True)


class Menu(models.Model):
    menu_id = models.AutoField(primary_key=True)
    menu_name = models.CharField(max_length=100)
    status = models.CharField(default='active', max_length=30, choices=status_choice)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


class FoodPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product', null=True, blank=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, db_column='menu', null=True, blank=True)
    center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
                                  null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(default='active', max_length=30, choices=status_choice)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)

