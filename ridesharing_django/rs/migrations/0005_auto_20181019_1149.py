# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-10-19 00:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rs', '0004_session_number_users'),
    ]

    operations = [
        migrations.RenameField(
            model_name='session',
            old_name='number_users',
            new_name='real_users',
        ),
        migrations.AddField(
            model_name='session',
            name='simulated_users',
            field=models.SmallIntegerField(default=0),
            preserve_default=False,
        ),
    ]