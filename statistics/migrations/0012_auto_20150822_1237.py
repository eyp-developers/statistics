# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0011_auto_20150820_1639'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activedebate',
            name='active_debate',
            field=models.CharField(max_length=8, null=True, blank=True),
        ),
    ]
