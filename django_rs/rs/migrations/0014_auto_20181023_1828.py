# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-10-23 07:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rs', '0013_auto_20181023_1826'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sessionuser',
            old_name='user_id',
            new_name='user',
        ),
    ]
