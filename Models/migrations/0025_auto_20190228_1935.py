# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2019-02-28 19:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Models', '0024_auto_20190228_1928'),
    ]

    operations = [
        migrations.RenameField(
            model_name='league',
            old_name='leagueFrequecy',
            new_name='leagueFrequency',
        ),
    ]
