# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2019-05-06 15:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Centers', '0016_centers_rvp'),
    ]

    operations = [
        migrations.AddField(
            model_name='centers',
            name='leagueAlcoholPer',
            field=models.FloatField(default=0),
        ),
    ]