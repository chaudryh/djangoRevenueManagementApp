# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-08-08 20:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Models', '0003_eventallocation_eventtier'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventallocation',
            name='row_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='eventtier',
            name='row_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='eventallocation',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='eventtier',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]