# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-08-08 19:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Models', '0002_productbase_productmodifier'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventAllocation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('category_id', models.IntegerField(blank=True, null=True)),
                ('group', models.CharField(blank=True, max_length=100, null=True)),
                ('category', models.CharField(blank=True, max_length=200, null=True)),
                ('product', models.CharField(blank=True, max_length=100, null=True)),
                ('sub_product', models.CharField(blank=True, max_length=100, null=True)),
                ('tier', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventTier',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('category_id', models.IntegerField(blank=True, null=True)),
                ('group', models.CharField(blank=True, max_length=100, null=True)),
                ('category', models.CharField(blank=True, max_length=200, null=True)),
                ('product', models.CharField(blank=True, max_length=100, null=True)),
                ('tier', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]
