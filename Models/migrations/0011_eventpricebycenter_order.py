# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-10-23 19:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Models', '0010_auto_20181022_1821'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventpricebycenter',
            name='order',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]