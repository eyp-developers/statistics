# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-21 19:57


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0031_announcement'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='announcement_type',
            field=models.CharField(choices=[(b'alert-success', b'Success'), (b'alert-info', b'Info'), (b'alert-warning', b'Warning'), (b'alert-danger', b'Danger')], default=b'alert-info', max_length=15),
        ),
    ]
