# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2019-04-17 13:23
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Audit', '0003_auto_20180622_1759'),
        ('Centers', '0016_centers_rvp'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Models', '0028_auto_20190307_1828'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeagueTransaction',
            fields=[
                ('transactKey', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('transactionNumber', models.IntegerField(blank=True, null=True)),
                ('leagueId', models.CharField(max_length=200)),
                ('businessDate', models.DateTimeField(blank=True, null=True)),
                ('timeOrder', models.DateTimeField(blank=True, null=True)),
                ('timeStart', models.DateTimeField(blank=True, null=True)),
                ('timeEnd', models.DateTimeField(blank=True, null=True)),
                ('bowlers', models.IntegerField(blank=True, null=True)),
                ('gameCount', models.IntegerField(blank=True, null=True)),
                ('revenueAmount', models.FloatField(blank=True, null=True)),
                ('leagueName', models.CharField(blank=True, max_length=500, null=True)),
                ('leagueType', models.CharField(blank=True, max_length=100, null=True)),
                ('leagueSubType', models.CharField(blank=True, max_length=100, null=True)),
                ('leagueStatus', models.CharField(blank=True, max_length=100, null=True)),
                ('dayOfWeekName', models.CharField(blank=True, max_length=100, null=True)),
                ('daysPerWeek', models.IntegerField(blank=True, null=True)),
                ('numberOfWeeks', models.IntegerField(blank=True, null=True)),
                ('start', models.DateTimeField(blank=True, null=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('leagueFrequency', models.CharField(blank=True, max_length=100, null=True)),
                ('appg', models.FloatField(blank=True, null=True)),
                ('rowHash', models.BinaryField(blank=True, null=True)),
                ('RowCreatedDate', models.DateTimeField(blank=True, null=True)),
                ('RowModifiedDate', models.DateTimeField(blank=True, null=True)),
                ('action_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('action_user', models.ForeignKey(blank=True, db_column='username', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
                ('centerId', models.ForeignKey(blank=True, db_column='centerNumber', null=True, on_delete=django.db.models.deletion.CASCADE, to='Centers.Centers')),
                ('tracking_id', models.ForeignKey(blank=True, db_column='tracking_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='Audit.Tracking')),
            ],
        ),
    ]
