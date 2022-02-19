# -*- coding: utf-8 -*-

from django.db import migrations

def fix_topic_overview_tuples(apps, schema_editor):
    Session = apps.get_model('statisticscore', 'Session')
    for session in Session.objects.all():
        if session.topic_overview_link == "('',)":
            session.topic_overview_link = ''
            session.save()

def reverse_fix_topic_overview_tuples(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('statisticscore', '0044_topic_overview_link'),
    ]

    operations = [
        migrations.RunPython(fix_topic_overview_tuples, reverse_fix_topic_overview_tuples)
    ]
