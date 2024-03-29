# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-24 12:31


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('statisticscore', '0021_auto_20150925_1648'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[(b'F', b'Female'), (b'M', b'Male'), (b'O', b'Other')], default=b'F', max_length=1)),
                ('committee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='statisticscore.Committee')),
            ],
        ),
    ]
