# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0010_session_session_is_visible'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='session_color',
            field=models.CharField(max_length=20),
        ),
    ]
