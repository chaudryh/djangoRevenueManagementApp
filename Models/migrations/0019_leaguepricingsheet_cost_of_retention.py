# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-12-14 21:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Models', '0018_rmps_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaguepricingsheet',
            name='cost_of_retention',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
