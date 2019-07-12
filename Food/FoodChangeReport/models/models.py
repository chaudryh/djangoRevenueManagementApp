from django.db import models
from django.utils import timezone
from accounts.models import User
from django.contrib.contenttypes.models import ContentType

import pytz
from dateutil import tz
import datetime

from Audit.models.models import *
from RM.Centers.models.models import *
from RM.Pricing.models.models import *
from RM.Food.models.models import *
from Food.FoodByCenter.models.models import Menu as Menu_


class FoodChangeReport(models.Model):
    report_id = models.AutoField(primary_key=True)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id', null=True, blank=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username', null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id', null=True, blank=True)
    menu_id = models.ForeignKey(Menu, on_delete=models.CASCADE, db_column='menu_id', null=True, blank=True)
    menu_id2 = models.ForeignKey(Menu_, on_delete=models.CASCADE, db_column='menu_id2', null=True, blank=True)
    center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
                                  null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    tier = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    price_old = models.FloatField(null=True, blank=True)
    price_new = models.FloatField(null=True, blank=True)
    product_start = models.DateField(null=True, blank=True)
    product_end = models.DateField(null=True, blank=True)
    email_notice = models.BooleanField(default=False)

