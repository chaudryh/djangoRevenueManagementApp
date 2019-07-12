from django.db import models
from django.utils import timezone
from accounts.models import User

import pytz
from dateutil import tz
import datetime

from configurations.config_models.models_choice import *

from Audit.models.models import *

# Create your models here.


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=100, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    all_day = models.BooleanField(default=True)
    status = models.CharField(default='active', max_length=30, choices=status_choice)
    email_notice = models.BooleanField(default=False)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)
