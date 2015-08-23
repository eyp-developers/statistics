# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0013_auto_20150823_1908'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='session_facebook_link',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='session_resolution_link',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='session_twitter_link',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='session_website_link',
            field=models.URLField(blank=True),
        ),
    ]
