# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0008_session_session_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='session_color',
            field=models.CharField(default='#fff', max_length=7),
            preserve_default=False,
        ),
    ]
