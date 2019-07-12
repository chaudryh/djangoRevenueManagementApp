from django.db import models
from django.utils import timezone
from accounts.models import User

import pytz
from dateutil import tz
import datetime

from configurations.config_models.models_choice import *
from Audit.models.models import *
# Create your models here.


class Centers(models.Model):

    center_id = models.CharField(max_length=100, primary_key=True)
    center_name = models.CharField(max_length=100, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    sale_region = models.CharField(max_length=100, null=True, blank=True)
    rvp = models.CharField(max_length=100, null=True, blank=True)
    territory = models.CharField(max_length=100, null=True, blank=True)
    arcade_type = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(default='open', max_length=30, choices=CentersChoice.status_choice)
    time_zone = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zipcode = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.CharField(max_length=100, null=True, blank=True)
    weather_point_id = models.CharField(max_length=100, null=True, blank=True)
    weekday_prime = models.CharField(max_length=100, null=True, blank=True)
    weekend_premium = models.CharField(max_length=100, null=True, blank=True)
    bowling_tier = models.CharField(max_length=100, null=True, blank=True)
    bowling_event_tier = models.CharField(max_length=100, null=True, blank=True)
    alcohol_tier = models.CharField(max_length=100, null=True, blank=True)
    food_tier = models.CharField(max_length=100, null=True, blank=True)
    food_menu = models.CharField(max_length=100, null=True, blank=True)
    food_kiosk = models.BooleanField(default=False)
    center_type = models.CharField(max_length=100, choices=CentersChoice.center_type_choice, null=True, blank=True)
    sunday_funday_bowling = models.FloatField(null=True, blank=True)
    sunday_funday_shoes = models.FloatField(null=True, blank=True)
    monday_mayhem = models.FloatField(null=True, blank=True)
    tuesday_222 = models.FloatField(null=True, blank=True)
    college_night_schedule = models.CharField(max_length=100, null=True, blank=True)
    college_night = models.FloatField(null=True, blank=True)
    college_night_wed = models.FloatField(null=True, blank=True)
    college_night_thu = models.FloatField(null=True, blank=True)
    leagueAlcoholPer = models.FloatField(default=0)
    lane = models.IntegerField(null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


class OpenHours(models.Model):
    #db_column is hard coded to avoid "center_id_id" being the column name. Null and blank ensures that during migration default values aren't needed.s
    center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
                                  null=True, blank=True)
    DOW = models.CharField(max_length=30, choices=DOW_choice, null=True, blank=True)
    open_hour = models.TimeField(null=True, blank=True)
    end_hour = models.TimeField(null=True, blank=True)
    overnight = models.BooleanField(default=False)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


# class Documents(models.Model):
#     name = models.CharField(max_length=100, null=True, blank=True, unique=True)
#     datetime = models.DateTimeField(default=timezone.now)
#     document = models.FileField(upload_to='Reports/ReportConfig/excel')
#     file_type = models.CharField(max_length=30, choices=file_type_choice, null=True, blank=True)
#     processor = models.CharField(max_length=50, choices=processor_choice, null=True, blank=True)
#     status = models.CharField(default='new', max_length=30, choices=document_status_choice)
#     created_by = models.ForeignKey(User, db_column='created_by', on_delete=models.CASCADE, default=1, related_name='ReportConfig')
#     created_on = models.DateTimeField(default=timezone.now)


