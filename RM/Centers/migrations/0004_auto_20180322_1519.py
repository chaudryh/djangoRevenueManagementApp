# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-22 15:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Centers', '0003_auto_20180322_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='centers',
            name='college_night_schedule',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
