# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-02-28 18:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0017_userpermission_date_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpermission',
            name='date_updated',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
