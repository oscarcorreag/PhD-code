# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-01-21 04:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=False)),
                ('min_lon', models.FloatField()),
                ('min_lat', models.FloatField()),
                ('max_lon', models.FloatField()),
                ('max_lat', models.FloatField()),
                ('travel_cost', models.FloatField(null=True)),
            ],
        ),
    ]
