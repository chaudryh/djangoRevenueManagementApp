# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2019-01-11 15:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Centers', '0015_centers_arcade_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='centers',
            name='rvp',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
