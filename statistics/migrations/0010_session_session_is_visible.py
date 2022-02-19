# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statisticscore', '0009_session_session_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='session_is_visible',
            field=models.BooleanField(default=True, verbose_name=b'is visible'),
            preserve_default=False,
        ),
    ]
