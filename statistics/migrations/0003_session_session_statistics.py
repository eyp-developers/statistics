# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0002_auto_20150810_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='session_statistics',
            field=models.CharField(default=b'SF', max_length=3, choices=[(b'S', b'Statistics Only'), (b'C', b'Point Content Only'), (b'JF', b'Single Form Statistics'), (b'SF', b'Split Form Statistics'), (b'N/A', b'No Statistics (Only Voting)')]),
        ),
    ]
