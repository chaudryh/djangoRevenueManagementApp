# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-04-02 13:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Centers', '0004_auto_20180322_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='centers',
            name='college_night_thu',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='centers',
            name='college_night_wed',
            field=models.FloatField(blank=True, null=True),
        ),
    ]