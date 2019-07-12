# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2019-04-25 12:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Centers', '0016_centers_rvp'),
        ('Audit', '0003_auto_20180622_1759'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Models', '0029_leaguetransaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeagueFood',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transactionNumber', models.IntegerField(blank=True, null=True)),
                ('openDate', models.DateField(blank=True, null=True)),
                ('revenueAmount', models.FloatField(blank=True, null=True)),
                ('avgRevenueAmount', models.FloatField(blank=True, null=True)),
                ('leagueCount', models.IntegerField(blank=True, null=True)),
                ('action_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('action_user', models.ForeignKey(blank=True, db_column='username', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
                ('centerId', models.ForeignKey(blank=True, db_column='centerNumber', null=True, on_delete=django.db.models.deletion.CASCADE, to='Centers.Centers')),
                ('tracking_id', models.ForeignKey(blank=True, db_column='tracking_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='Audit.Tracking')),
            ],
        ),
        migrations.CreateModel(
            name='LeagueTransactionSummary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leagueId', models.CharField(max_length=200)),
                ('bowlers', models.IntegerField(blank=True, null=True)),
                ('game', models.IntegerField(blank=True, null=True)),
                ('revenue', models.FloatField(blank=True, null=True)),
                ('transaction', models.IntegerField(blank=True, null=True)),
                ('action_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('action_user', models.ForeignKey(blank=True, db_column='username', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
                ('centerId', models.ForeignKey(blank=True, db_column='centerNumber', null=True, on_delete=django.db.models.deletion.CASCADE, to='Centers.Centers')),
                ('tracking_id', models.ForeignKey(blank=True, db_column='tracking_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='Audit.Tracking')),
            ],
        ),
    ]
