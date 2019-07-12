# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-06-06 17:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Centers', '0009_centers_weather_sync'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='centers',
            name='noaa_weather_station_id',
        ),
        migrations.RemoveField(
            model_name='centers',
            name='weather_sync',
        ),
        migrations.AddField(
            model_name='centers',
            name='weather_point_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]