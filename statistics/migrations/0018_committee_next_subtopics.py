# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statisticscore', '0017_auto_20150825_0026'),
    ]

    operations = [
        migrations.AddField(
            model_name='committee',
            name='next_subtopics',
            field=models.ManyToManyField(related_name='next_subtopics+', to='statisticscore.SubTopic', blank=True),
        ),
    ]
