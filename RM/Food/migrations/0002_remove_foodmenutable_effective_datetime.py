# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-22 18:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Food', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='foodmenutable',
            name='effective_datetime',
        ),
    ]
