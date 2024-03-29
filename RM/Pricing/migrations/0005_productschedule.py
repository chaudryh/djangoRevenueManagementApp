# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-04-09 14:23
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Audit', '0002_tracking_username'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Pricing', '0004_auto_20180406_1413'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(blank=True, null=True)),
                ('DOW', models.CharField(blank=True, choices=[('mon', 'mon'), ('tue', 'tue'), ('wed', 'wed'), ('thu', 'thu'), ('fri', 'fri'), ('sat', 'sat'), ('sun', 'sun')], max_length=30, null=True)),
                ('start', models.DateTimeField(blank=True, null=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('freq', models.CharField(blank=True, choices=[('Once', 'Once'), ('Anually', 'Anually'), ('Weekly', 'Weekly'), ('Daily', 'Daily')], max_length=30, null=True)),
                ('status', models.CharField(choices=[('active', 'active'), ('inactive', 'inactive')], default='inactive', max_length=30)),
                ('product_name', models.CharField(blank=True, max_length=100, null=True)),
                ('action_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('action_user', models.ForeignKey(blank=True, db_column='username', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
                ('product_id', models.ForeignKey(blank=True, db_column='product_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='Pricing.Product')),
                ('tracking_id', models.ForeignKey(blank=True, db_column='tracking_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='Audit.Tracking')),
            ],
        ),
    ]
