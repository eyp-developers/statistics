# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='committee',
            name='committee_name',
            field=models.CharField(max_length=8),
        ),
    ]
