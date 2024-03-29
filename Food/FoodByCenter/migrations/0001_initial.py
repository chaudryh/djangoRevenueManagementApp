# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2019-03-25 17:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Pricing', '0016_auto_20180718_1805'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Centers', '0016_centers_rvp'),
        ('Audit', '0003_auto_20180622_1759'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(blank=True, max_length=100, null=True)),
                ('price', models.FloatField(blank=True, null=True)),
                ('start', models.DateTimeField(blank=True, null=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('action_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('action_user', models.ForeignKey(blank=True, db_column='username', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
                ('center_id', models.ForeignKey(blank=True, db_column='center_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='Centers.Centers')),
            ],
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('menu_id', models.AutoField(primary_key=True, serialize=False)),
                ('menu_name', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('active', 'active'), ('inactive', 'inactive')], default='active', max_length=30)),
                ('action_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('action_user', models.ForeignKey(blank=True, db_column='username', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
                ('tracking_id', models.ForeignKey(blank=True, db_column='tracking_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='Audit.Tracking')),
            ],
        ),
        migrations.AddField(
            model_name='foodprice',
            name='menu',
            field=models.ForeignKey(blank=True, db_column='menu', null=True, on_delete=django.db.models.deletion.CASCADE, to='FoodByCenter.Menu'),
        ),
        migrations.AddField(
            model_name='foodprice',
            name='product',
            field=models.ForeignKey(blank=True, db_column='product', null=True, on_delete=django.db.models.deletion.CASCADE, to='Pricing.Product'),
        ),
        migrations.AddField(
            model_name='foodprice',
            name='tracking_id',
            field=models.ForeignKey(blank=True, db_column='tracking_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='Audit.Tracking'),
        ),
    ]
