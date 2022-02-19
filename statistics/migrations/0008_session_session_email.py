# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statisticscore', '0007_auto_20150817_0000'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='session_email',
            field=models.EmailField(default='oliver@stenbom.eu', max_length=254),
            preserve_default=False,
        ),
    ]
