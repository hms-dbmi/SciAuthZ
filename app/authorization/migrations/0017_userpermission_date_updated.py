# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-01-17 18:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0016_auto_20180116_1755'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpermission',
            name='date_updated',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]