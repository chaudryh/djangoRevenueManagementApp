# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-11-19 19:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Audit', '0003_auto_20180622_1759'),
        ('Centers', '0015_centers_arcade_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Models', '0012_auto_20181024_1511'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaguePricingSheet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bowleroM', models.CharField(blank=True, max_length=200, null=True)),
                ('min_lineage_fee_bowlero', models.FloatField(blank=True, null=True)),
                ('max_lineage_fee_bowlero', models.FloatField(blank=True, null=True)),
                ('max_cover', models.FloatField(blank=True, null=True)),
                ('cost_of_acquisition', models.FloatField(blank=True, null=True)),
                ('max_ceiling_customer_fund', models.FloatField(blank=True, null=True)),
                ('actualPF', models.FloatField(blank=True, null=True)),
                ('share_of_PF_bowlero', models.FloatField(blank=True, null=True)),
                ('share_of_PF_treasurer', models.FloatField(blank=True, null=True)),
                ('action_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('action_user', models.ForeignKey(blank=True, db_column='username', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
                ('center_id', models.ForeignKey(blank=True, db_column='center_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='Centers.Centers')),
                ('tracking_id', models.ForeignKey(blank=True, db_column='tracking_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='Audit.Tracking')),
            ],
        ),
    ]
