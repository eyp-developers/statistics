# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-24 12:37


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statisticscore', '0022_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='gender',
            name='timestamp',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
