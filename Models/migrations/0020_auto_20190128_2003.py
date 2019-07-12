# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2019-01-28 20:03
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Audit', '0003_auto_20180622_1759'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Centers', '0016_centers_rvp'),
        ('Models', '0019_leaguepricingsheet_cost_of_retention'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeagueNew',
            fields=[
                ('leagueId', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('leagueIdCopied', models.CharField(blank=True, max_length=200, null=True)),
                ('leagueName', models.CharField(blank=True, max_length=500, null=True)),
                ('leagueType', models.CharField(blank=True, max_length=100, null=True)),
                ('leagueSubType', models.CharField(blank=True, max_length=100, null=True)),
                ('leagueStatus', models.CharField(blank=True, max_length=100, null=True)),
                ('dayOfWeekName', models.CharField(blank=True, max_length=100, null=True)),
                ('daysPerWeek', models.IntegerField(blank=True, null=True)),
                ('numberOfWeeks', models.IntegerField(blank=True, null=True)),
                ('start', models.DateTimeField(blank=True, null=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('startingLaneNumber', models.CharField(blank=True, max_length=100, null=True)),
                ('endingLaneNumber', models.CharField(blank=True, max_length=100, null=True)),
                ('bowlerEquivalentGoal', models.IntegerField(blank=True, null=True)),
                ('confirmedBowlerCount', models.IntegerField(blank=True, null=True)),
                ('currentYearLeagueNumber', models.CharField(blank=True, max_length=100, null=True)),
                ('playersPerTeam', models.IntegerField(blank=True, null=True)),
                ('numberOfTeams', models.IntegerField(blank=True, null=True)),
                ('gamesPerPlayer', models.IntegerField(blank=True, null=True)),
                ('lineageCost', models.FloatField(blank=True, null=True)),
                ('action_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('action_user', models.ForeignKey(blank=True, db_column='username', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
                ('centerId', models.ForeignKey(blank=True, db_column='center_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='Centers.Centers')),
                ('tracking_id', models.ForeignKey(blank=True, db_column='tracking_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='Audit.Tracking')),
            ],
        ),
        migrations.RemoveField(
            model_name='league',
            name='action_user',
        ),
        migrations.RemoveField(
            model_name='league',
            name='center_id',
        ),
        migrations.RemoveField(
            model_name='league',
            name='tracking_id',
        ),
        migrations.DeleteModel(
            name='League',
        ),
    ]
