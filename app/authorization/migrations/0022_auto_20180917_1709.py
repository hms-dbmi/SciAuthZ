# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-09-17 17:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0021_remove_userpermission_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userpermissionrequest',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserPermissionRequest',
        ),
    ]
