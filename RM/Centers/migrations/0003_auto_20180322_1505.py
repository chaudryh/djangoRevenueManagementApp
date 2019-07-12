# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-22 15:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Centers', '0002_auto_20180321_1354'),
    ]

    operations = [
        migrations.AddField(
            model_name='centers',
            name='college_night',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='centers',
            name='college_night_schedule',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='centers',
            name='monday_mayhem',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='centers',
            name='sunday_funday_bowling',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='centers',
            name='sunday_funday_shoes',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='centers',
            name='tuesday_222',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
