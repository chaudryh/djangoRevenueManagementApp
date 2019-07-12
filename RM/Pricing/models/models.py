from django.db import models
from django.utils import timezone

import pytz
from dateutil import tz
import datetime

from configurations.config_models.models_choice import *

from RM.Centers.models.models import *
from accounts.models import *
# Create your models here.


# Products
class Product(models.Model):

    product_id = models.CharField(max_length=100, primary_key=True)
    product_name = models.CharField(max_length=100, null=True, blank=True)
    readable_product_name = models.CharField(max_length=100, null=True, blank=True)
    short_product_name = models.CharField(max_length=100, null=True, blank=True)
    report_type = models.CharField(max_length=100, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    status = models.CharField(default='active', max_length=30, choices=ProductChoice.product_status_choice)
    bundle_id = models.CharField(max_length=100, null=True, blank=True)
    bundle_name = models.CharField(max_length=100, null=True, blank=True)
    always_opt_in = models.CharField(max_length=100, null=True, blank=True)
    # Pixel fields
    product_num = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    report_num = models.CharField(max_length=100, null=True, blank=True)
    # End
    sell_type = models.CharField(max_length=100, default='retail')
    center_type = models.CharField(max_length=100,choices=CentersChoice.center_type_choice, null=True, blank=True)
    period = models.CharField(max_length=100, null=True, blank=True)
    # business_date = models.DateTimeField(default=timezone.now)
    # center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
    #                               )

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


# Centers Products Opt In / Out
class ProductOpt(models.Model):

    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, to_field='product_id', db_column='product_id',
                                   null=True, blank=True)
    center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
                                  null=True, blank=True)
    opt = models.CharField(max_length=100, choices=ProductChoice.product_opt_choice, null=True, blank=True)
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


# Period
#not being used
class Period(models.Model):
    category = models.CharField(max_length=100, default='dayparts')
    period_label = models.CharField(max_length=100, default='non-prime')
    DOW = models.CharField(max_length=30, choices=DOW_choice, null=True, blank=True)
    effective_datetime = models.DateTimeField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    overnight = models.BooleanField(default=False)
    status = models.CharField(default='inactive', max_length=30, choices=status_choice)
    center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
                                  null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


# Price
#not being used
class RetailBowlingPriceOld(models.Model):

    price = models.FloatField()
    unit_type = models.CharField(default='by_unit', max_length=30, choices=PricingChoice.unit_type)
    effective_datetime = models.DateTimeField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    overnight = models.BooleanField(default=False)
    status = models.CharField(default='inactive', max_length=30, choices=status_choice)
    DOW = models.CharField(max_length=30, choices=DOW_choice, null=True, blank=True)
    center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
                                  null=True, blank=True)
    period = models.ForeignKey(Period, on_delete=models.CASCADE, null=True, blank=True)
    period_label = models.CharField(max_length=100, null=True, blank=True)
    product_name = models.CharField(max_length=100, null=True, blank=True)
    create_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    create_datetime = models.DateTimeField(default=timezone.now)

#not being used
class RetailShoePriceOld(models.Model):

    price = models.FloatField()
    unit_type = models.CharField(default='by_unit', max_length=30, choices=PricingChoice.unit_type)
    effective_datetime = models.DateTimeField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    overnight = models.BooleanField(default=False)
    status = models.CharField(default='inactive', max_length=30, choices=status_choice)
    DOW = models.CharField(max_length=30, choices=DOW_choice, null=True, blank=True)
    center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
                                  null=True, blank=True)
    period = models.ForeignKey(Period, on_delete=models.CASCADE, null=True, blank=True)
    period_label = models.CharField(max_length=100, null=True, blank=True)
    product_name = models.CharField(max_length=100, null=True, blank=True)
    create_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    create_datetime = models.DateTimeField(default=timezone.now)

#not being used
class PricingTierTable(models.Model):
    price = models.FloatField()
    tier = models.CharField(max_length=100, null=True, blank=True)
    DOW = models.CharField(max_length=30, choices=DOW_choice, null=True, blank=True)
    time = models.CharField(max_length=100, null=True, blank=True)
    start = models.TimeField(null=True, blank=True)
    end = models.TimeField(null=True, blank=True)
    period_label = models.CharField(max_length=100, null=True, blank=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, to_field='product_id', db_column='product_id',
                                   null=True, blank=True)
    product_name = models.CharField(max_length=100, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    center_type = models.CharField(max_length=100, choices=CentersChoice.center_type_choice, null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)

#not being used
class ProductWeeklySchedule(models.Model):
    price = models.FloatField(null=True, blank=True)
    schedule_num = models.CharField(max_length=30, default=1)
    effective_datetime = models.DateTimeField(default=timezone.now)
    DOW_transact = models.CharField(max_length=30, choices=DOW_choice, null=True, blank=True)
    DOW_business_start = models.CharField(max_length=30, choices=DOW_choice, null=True, blank=True)
    DOW_business_end = models.CharField(max_length=30, choices=DOW_choice, null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(default='inactive', max_length=30, choices=status_choice)
    center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
                                  null=True, blank=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id', null=True, blank=True)
    product_name = models.CharField(max_length=100, null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)

#not being used
class RetailBowlingPrice(models.Model):

    date = models.DateField(default=timezone.now)
    DOW = models.CharField(max_length=30, choices=DOW_choice, null=True, blank=True)
    center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
                                  null=True, blank=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id', null=True, blank=True)
    product_name = models.CharField(max_length=100, null=True, blank=True)
    schedule = models.ForeignKey(ProductWeeklySchedule, on_delete=models.CASCADE, to_field='id', db_column='schedule_id',
                                 null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    perpetual = models.BooleanField(default=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)

#not being used
class RetailShoePrice(models.Model):

    date = models.DateField(default=timezone.now)
    DOW = models.CharField(max_length=30, choices=DOW_choice, null=True, blank=True)
    center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
                                  null=True, blank=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id', null=True, blank=True)
    product_name = models.CharField(max_length=100, null=True, blank=True)
    schedule = models.ForeignKey(ProductWeeklySchedule, on_delete=models.CASCADE, to_field='id', db_column='schedule_id',
                                  null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    perpetual = models.BooleanField(default=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


class ProductPrice(models.Model):

    date = models.DateField(default=timezone.now)
    DOW = models.CharField(max_length=30, choices=DOW_choice, null=True, blank=True)
    center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
                                  null=True, blank=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id', null=True, blank=True)
    product_name = models.CharField(max_length=100, null=True, blank=True)
    schedule = models.ForeignKey(ProductWeeklySchedule, on_delete=models.CASCADE, to_field='id', db_column='schedule_id',
                                  null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    perpetual = models.BooleanField(default=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


class ProductSchedule(models.Model):
    price = models.FloatField(null=True, blank=True)
    DOW = models.CharField(max_length=30, choices=DOW_choice, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    freq = models.CharField(max_length=30, choices=ProductScheduleChoice.freq_choice, null=True, blank=True)
    status = models.CharField(default='inactive', max_length=30, choices=status_choice)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id', null=True, blank=True)
    product_name = models.CharField(max_length=100, null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


class Bundle(models.Model):
    bundle_id = models.AutoField(primary_key=True)
    bundle_name = models.CharField(max_length=100, choices=DOW_choice, null=True, blank=True)


class BundleProduct(models.Model):
    bundle_id = models.ForeignKey(Bundle, on_delete=models.CASCADE, to_field='bundle_id', db_column='bundle_id',
                                  null=True, blank=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, to_field='product_id', db_column='product_id',
                                   null=True, blank=True)