# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2019-02-28 19:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Models', '0022_league_last'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='frequency',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
