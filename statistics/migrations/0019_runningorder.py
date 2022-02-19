# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statisticscore', '0018_committee_next_subtopics'),
    ]

    operations = [
        migrations.CreateModel(
            name='RunningOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.PositiveSmallIntegerField()),
                ('point_type', models.CharField(default=b'P', max_length=5, choices=[(b'P', b'Point'), (b'DR', b'Direct Response')])),
                ('committee_by', models.ForeignKey(on_delete=models.deletion.CASCADE, to='statisticscore.Committee')),
                ('session', models.ForeignKey(on_delete=models.deletion.CASCADE, to='statisticscore.Session')),
            ],
        ),
    ]
