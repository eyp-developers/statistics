# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0004_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentpoint',
            name='point_type',
            field=models.CharField(default=b'P', max_length=2, choices=[(b'P', b'Point'), (b'DR', b'Direct Response')]),
        ),
    ]
