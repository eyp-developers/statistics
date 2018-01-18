# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0020_auto_20150925_1646'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='session_rounds_enabled',
        ),
        migrations.RemoveField(
            model_name='session',
            name='session_subtopics_enabled',
        ),
    ]
