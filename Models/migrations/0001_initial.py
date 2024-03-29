# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-07-17 16:49
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Audit', '0003_auto_20180622_1759'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Centers', '0012_centers_bowling_event_tier'),
        ('Pricing', '0015_auto_20180705_1601'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductPriceChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField(blank=True, null=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('product_name', models.CharField(blank=True, max_length=100, null=True)),
                ('price', models.FloatField(blank=True, null=True)),
                ('perpetual', models.BooleanField(default=True)),
                ('action_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('action_user', models.ForeignKey(blank=True, db_column='username', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
                ('center_id', models.ForeignKey(blank=True, db_column='center_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='Centers.Centers')),
                ('product_id', models.ForeignKey(blank=True, db_column='product_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='Pricing.Product')),
                ('tracking_id', models.ForeignKey(blank=True, db_column='tracking_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='Audit.Tracking')),
            ],
        ),
        migrations.AddField(
            model_name='productpricechange',
            name='DOW',
            field=models.CharField(blank=True, choices=[('mon', 'mon'), ('tue', 'tue'), ('wed', 'wed'), ('thu', 'thu'),
                                                        ('fri', 'fri'), ('sat', 'sat'), ('sun', 'sun')], max_length=30,
                                   null=True),
        ),
        migrations.AddField(
            model_name='productpricechange',
            name='end_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='productpricechange',
            name='modifier_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='productpricechange',
            name='product_base_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='productpricechange',
            name='start_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
