# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-04-23 19:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pricing', '0006_auto_20180423_1758'),
    ]

    operations = [
        migrations.AddField(
            model_name='pricingtiertable',
            name='end',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pricingtiertable',
            name='start',
            field=models.TimeField(blank=True, null=True),
        ),
    ]