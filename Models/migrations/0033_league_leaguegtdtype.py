# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2019-05-08 20:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Models', '0032_remove_leaguealocohol_transactionnumber'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='leagueGtdType',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
