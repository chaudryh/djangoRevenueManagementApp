# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-04 14:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pricing', '0007_auto_20180423_1905'),
    ]

    operations = [
        migrations.AddField(
            model_name='pricingtiertable',
            name='center_type',
            field=models.CharField(blank=True, choices=[('traditional', 'traditional'), ('experiential', 'experiential'), ('session', 'session')], max_length=100, null=True),
        ),
    ]
