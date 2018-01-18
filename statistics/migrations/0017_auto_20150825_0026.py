# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0016_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='session_admin_user',
            field=models.ForeignKey(related_name='session_admin', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='session_submission_user',
            field=models.ForeignKey(related_name='session_submit', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
