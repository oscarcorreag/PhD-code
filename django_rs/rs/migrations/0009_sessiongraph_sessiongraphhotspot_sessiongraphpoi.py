# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-10-23 02:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rs', '0008_auto_20181023_1055'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionGraph',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('edge_i', models.BigIntegerField()),
                ('edge_j', models.BigIntegerField()),
                ('session_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rs.Session')),
            ],
        ),
        migrations.CreateModel(
            name='SessionGraphHotspot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hotspot', models.BigIntegerField()),
                ('session_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rs.Session')),
            ],
        ),
        migrations.CreateModel(
            name='SessionGraphPoi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('poi', models.BigIntegerField()),
                ('session_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rs.Session')),
            ],
        ),
    ]
