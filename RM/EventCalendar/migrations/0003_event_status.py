# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-08 15:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EventCalendar', '0002_event_event_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='status',
            field=models.CharField(choices=[('active', 'active'), ('inactive', 'inactive')], default='active', max_length=30),
        ),
    ]
