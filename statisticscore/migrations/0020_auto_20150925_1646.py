# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statisticscore', '0019_runningorder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='session_statistics',
            field=models.CharField(default=b'JF', max_length=5, choices=[(b'S', b'Statistics Only'), (b'C', b'Point Content Only'), (b'JF', b'Joint Form Statistics'), (b'SF', b'Split Form Statistics'), (b'R', b'Running Order Statistics'), (b'RC', b'Running Order Statistics with Point Content')]),
        ),
    ]
