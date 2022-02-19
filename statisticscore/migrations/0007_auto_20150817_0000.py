# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statisticscore', '0006_auto_20150816_2359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='session_statistics',
            field=models.CharField(default=b'JF', max_length=5, choices=[(b'S', b'Statistics Only'), (b'C', b'Point Content Only'), (b'JF', b'Joint Form Statistics'), (b'SF', b'Split Form Statistics'), (b'N/A', b'No Statistics (Only Voting)')]),
        ),
    ]
