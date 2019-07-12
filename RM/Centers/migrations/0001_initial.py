# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-21 13:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Centers',
            fields=[
                ('center_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('center_name', models.CharField(blank=True, max_length=100, null=True)),
                ('brand', models.CharField(blank=True, max_length=100, null=True)),
                ('region', models.CharField(blank=True, max_length=100, null=True)),
                ('district', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(choices=[('open', 'open'), ('closed', 'closed')], default='open', max_length=30)),
                ('time_zone', models.CharField(blank=True, max_length=100, null=True)),
                ('address', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('zipcode', models.CharField(blank=True, max_length=100, null=True)),
                ('weekday_prime', models.CharField(blank=True, max_length=100, null=True)),
                ('weekend_premium', models.CharField(blank=True, max_length=100, null=True)),
                ('bowling_tier', models.CharField(blank=True, max_length=100, null=True)),
                ('alcohol_tier', models.CharField(blank=True, max_length=100, null=True)),
                ('food_tier', models.CharField(blank=True, max_length=100, null=True)),
                ('food_menu', models.CharField(blank=True, max_length=100, null=True)),
                ('food_kiosk', models.BooleanField(default=False)),
                ('center_type', models.CharField(blank=True, choices=[('traditional', 'traditional'), ('experiential', 'experiential')], max_length=100, null=True)),
                ('action_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='OpenHours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DOW', models.CharField(blank=True, choices=[('mon', 'mon'), ('tue', 'tue'), ('wed', 'wed'), ('thu', 'thu'), ('fri', 'fri'), ('sat', 'sat'), ('sun', 'sun')], max_length=30, null=True)),
                ('open_hour', models.TimeField()),
                ('end_hour', models.TimeField()),
                ('overnight', models.BooleanField(default=False)),
                ('action_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]