from django.db import models
from django.utils import timezone

import pytz
from dateutil import tz
import datetime

from configurations.config_models.models_choice import *

from RM.Centers.models.models import *
from RM.Pricing.models.models import *
from accounts.models import *


# Create your models here.

# Product
class ProductPriceChange(models.Model):

    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    DOW = models.CharField(max_length=30, choices=DOW_choice, null=True, blank=True)
    center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
                                  null=True, blank=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id', null=True, blank=True)
    product_name = models.CharField(max_length=100, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    perpetual = models.BooleanField(default=True)

    # Event
    product_base_id = models.CharField(max_length=200, null=True, blank=True)
    modifier_id = models.CharField(max_length=200, null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


# Events
class EventTier(models.Model):
    order = models.IntegerField(null=True, blank=True)
    group = models.CharField(max_length=100, null=True, blank=True)
    subGroup = models.CharField(max_length=200, null=True, blank=True)
    product = models.CharField(max_length=100, null=True, blank=True)
    tier = models.CharField(max_length=100, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


class EventAllocation(models.Model):
    order = models.IntegerField(null=True, blank=True)
    group = models.CharField(max_length=100, null=True, blank=True)
    subGroup = models.CharField(max_length=200, null=True, blank=True)
    product = models.CharField(max_length=100, null=True, blank=True)
    subProduct = models.CharField(max_length=100, null=True, blank=True)
    tier = models.CharField(max_length=100, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


class EventPriceByCenter(models.Model):
    group = models.CharField(max_length=100, null=True, blank=True)
    product = models.CharField(max_length=100, null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True)
    center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
                                  null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


class EventPromo(models.Model):
    promo_code = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    eventByDate = models.DateField(null=True, blank=True)
    comment = models.CharField(max_length=500, null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


class EventCenterTier(models.Model):
    center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
                                  null=True, blank=True)
    product = models.CharField(max_length=100, null=True, blank=True)
    tier = models.CharField(max_length=100, null=True, blank=True)
    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


class RMPS(models.Model):
    center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
                                  null=True, blank=True)
    pdf_link = models.CharField(max_length=100, null=True, blank=True)
    attribute = models.CharField(max_length=100, null=True, blank=True)
    value = models.CharField(max_length=100, null=True, blank=True)
    unit = models.CharField(max_length=100, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


# GEMS
class ProductBase(models.Model):

    product_base_id = models.CharField(max_length=200, primary_key=True)
    product_base_name = models.CharField(max_length=200, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=200, null=True, blank=True)
    package = models.CharField(max_length=200, null=True, blank=True)
    pricing_tier = models.CharField(max_length=200, null=True, blank=True)
    product_name = models.CharField(max_length=200, null=True, blank=True)
    product_category = models.CharField(max_length=200, null=True, blank=True)
    hide_from_online_customers = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=200, null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


class ProductModifier(models.Model):

    modifier_id = models.CharField(max_length=200, primary_key=True)
    modifier_name = models.CharField(max_length=200, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    price_percent = models.FloatField(null=True, blank=True)
    product_base_name = models.CharField(max_length=200, null=True, blank=True)

    dow = models.CharField(max_length=200, null=True, blank=True)
    start_hour = models.IntegerField(null=True, blank=True)
    start_min = models.IntegerField(null=True, blank=True)
    end_hour = models.IntegerField(null=True, blank=True)
    end_min = models.IntegerField(null=True, blank=True)
    start_event_date = models.CharField(max_length=200, null=True, blank=True)
    end_event_date = models.CharField(max_length=200, null=True, blank=True)
    start_day_of_month = models.CharField(max_length=200, null=True, blank=True)
    end_day_of_month = models.CharField(max_length=200, null=True, blank=True)
    start_month = models.CharField(max_length=200, null=True, blank=True)
    end_month = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=200, null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


# League
class LeaguePricingSheet(models.Model):

    center_id = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
                                  null=True, blank=True)
    bowleroM = models.CharField(max_length=200, null=True, blank=True)
    min_lineage_fee_bowlero = models.FloatField(null=True, blank=True)
    max_lineage_fee_bowlero = models.FloatField(null=True, blank=True)
    max_cover = models.FloatField(null=True, blank=True)
    cost_of_acquisition = models.FloatField(null=True, blank=True)
    cost_of_retention = models.FloatField(null=True, blank=True)
    max_ceiling_customer_fund = models.FloatField(null=True, blank=True)
    actualPF = models.FloatField(null=True, blank=True)
    share_of_PF_bowlero = models.FloatField(null=True, blank=True)
    share_of_PF_treasurer = models.FloatField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


class League(models.Model):
    leagueId = models.CharField(max_length=200, primary_key=True)
    leagueIdCopied = models.CharField(max_length=200, null=True, blank=True)
    centerId = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='center_id',
                                  null=True, blank=True)
    leagueName = models.CharField(max_length=500, null=True, blank=True)
    leagueType = models.CharField(max_length=100, null=True, blank=True)
    leagueSubType = models.CharField(max_length=100, null=True, blank=True)
    leagueGtdType = models.CharField(max_length=100, null=True, blank=True)
    leagueStatus = models.CharField(max_length=100, null=True, blank=True)
    dayOfWeekName = models.CharField(max_length=100, null=True, blank=True)
    daysPerWeek = models.IntegerField(null=True, blank=True)
    numberOfWeeks = models.IntegerField(null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    startingLaneNumber = models.CharField(max_length=100, null=True, blank=True)
    endingLaneNumber = models.CharField(max_length=100, null=True, blank=True)
    bowlerEquivalentGoal = models.IntegerField(null=True, blank=True)
    confirmedBowlerCount = models.IntegerField(null=True, blank=True)
    currentYearLeagueNumber = models.CharField(max_length=100, null=True, blank=True)
    playersPerTeam = models.IntegerField(null=True, blank=True)
    numberOfTeams = models.IntegerField(null=True, blank=True)
    gamesPerPlayer = models.IntegerField(null=True, blank=True)
    lineageCost = models.FloatField(null=True, blank=True)
    last = models.BooleanField(default=False)
    leagueFrequency = models.CharField(max_length=100, null=True, blank=True)
    rowHash = models.BinaryField(null=True, blank=True)
    RowCreatedDate = models.DateTimeField(null=True, blank=True)
    RowModifiedDate = models.DateTimeField(null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


class LeagueTransaction(models.Model):
    transactKey = models.CharField(max_length=200, primary_key=True)
    transactionNumber = models.IntegerField(null=True, blank=True)
    leagueId = models.CharField(max_length=200)
    centerId = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='centerNumber',
                                 null=True, blank=True)
    businessDate = models.DateTimeField(null=True, blank=True)
    timeOrder = models.DateTimeField(null=True, blank=True)
    timeStart = models.DateTimeField(null=True, blank=True)
    timeEnd = models.DateTimeField(null=True, blank=True)
    bowlers = models.IntegerField(null=True, blank=True)
    gameCount = models.IntegerField(null=True, blank=True)
    revenueAmount = models.FloatField(null=True, blank=True)
    # LMA
    leagueName = models.CharField(max_length=500, null=True, blank=True)
    leagueType = models.CharField(max_length=100, null=True, blank=True)
    leagueSubType = models.CharField(max_length=100, null=True, blank=True)
    leagueStatus = models.CharField(max_length=100, null=True, blank=True)
    dayOfWeekName = models.CharField(max_length=100, null=True, blank=True)
    daysPerWeek = models.IntegerField(null=True, blank=True)
    numberOfWeeks = models.IntegerField(null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    leagueFrequency = models.CharField(max_length=100, null=True, blank=True)
    appg = models.FloatField(null=True, blank=True)
    rowHash = models.BinaryField(null=True, blank=True)
    RowCreatedDate = models.DateTimeField(null=True, blank=True)
    RowModifiedDate = models.DateTimeField(null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


class LeagueTransactionSummary(models.Model):
    leagueId = models.CharField(max_length=200)
    centerId = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='centerNumber',
                                 null=True, blank=True)
    bowlers = models.IntegerField(null=True, blank=True)
    game = models.IntegerField(null=True, blank=True)
    revenue = models.FloatField(null=True, blank=True)
    transaction = models.IntegerField(null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


class LeagueFood(models.Model):
    centerId = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='centerNumber',
                                 null=True, blank=True)
    transactionNumber = models.IntegerField(null=True, blank=True)

    openDate = models.DateField(null=True, blank=True)
    revenueAmount = models.FloatField(null=True, blank=True)
    avgRevenueAmount = models.FloatField(null=True, blank=True)
    leagueCount = models.IntegerField(null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)


class LeagueAlocohol(models.Model):
    centerId = models.ForeignKey(Centers, on_delete=models.CASCADE, to_field='center_id', db_column='centerNumber',
                                 null=True, blank=True)
    openDate = models.DateField(null=True, blank=True)
    revenueAmount = models.FloatField(null=True, blank=True)
    avgRevenueAmount = models.FloatField(null=True, blank=True)
    leagueCount = models.IntegerField(null=True, blank=True)

    # Tracking
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username', db_column='username',
                                    null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    tracking_id = models.ForeignKey(Tracking, on_delete=models.CASCADE, to_field='tracking_id', db_column='tracking_id',
                                    null=True, blank=True)
