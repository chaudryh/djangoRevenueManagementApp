# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2019-03-07 18:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Models', '0027_auto_20190307_1827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='rowHash',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]