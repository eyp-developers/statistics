# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statisticscore', '0014_auto_20150823_1909'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='session_has_technical_problems',
            field=models.BooleanField(default=False, verbose_name=b'session has technical problems'),
        ),
    ]
