# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statisticscore', '0002_auto_20150810_1524'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active_debate', models.CharField(max_length=8)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('point_content', models.TextField()),
                ('committee_by', models.ForeignKey(on_delete=models.deletion.CASCADE, to='statisticscore.Committee')),
                ('session', models.ForeignKey(on_delete=models.deletion.CASCADE, to='statisticscore.Session')),
            ],
        ),
        migrations.AlterField(
            model_name='point',
            name='active_debate',
            field=models.CharField(max_length=8, null=True, blank=True),
        ),
    ]
