# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2019-02-07 17:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BSChangeReport', '0006_bschangereport_email_notice'),
    ]

    operations = [
        migrations.AddField(
            model_name='bschangereport',
            name='product_RMPS',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
