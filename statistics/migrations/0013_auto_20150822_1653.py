# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0012_auto_20150822_1237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='active_debate',
            field=models.CharField(max_length=8),
        ),
    ]
