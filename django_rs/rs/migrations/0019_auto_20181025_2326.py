# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-10-25 12:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rs', '0018_sessionactivity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='session',
            old_name='centroid_lat',
            new_name='max_lat',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='centroid_lon',
            new_name='max_lon',
        ),
        migrations.RenameField(
            model_name='sessionplandetail',
            old_name='edge_i',
            new_name='node_i',
        ),
        migrations.RenameField(
            model_name='sessionplandetail',
            old_name='edge_j',
            new_name='node_j',
        ),
        migrations.AddField(
            model_name='session',
            name='min_lat',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='session',
            name='min_lon',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]