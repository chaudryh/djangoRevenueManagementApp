# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-04-23 17:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Centers', '0005_auto_20180402_1313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='centers',
            name='center_type',
            field=models.CharField(blank=True, choices=[('traditional', 'traditional'), ('experiential', 'experiential'), ('session', 'session')], max_length=100, null=True),
        ),
    ]
