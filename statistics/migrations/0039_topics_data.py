# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-12-23 12:42

from django.db import migrations


def save_topics(apps, schema_editor):
    Committee = apps.get_model('statisticscore', 'Committee')
    Topic = apps.get_model('statisticscore', 'Topic')
    StatisticsTopicPlace = apps.get_model('statisticscore', 'StatisticsTopicPlace')
    for committee in Committee.objects.all():
        topic_text = committee.topic_text
        if Topic.objects.filter(text=topic_text).exists():
            topic = Topic.objects.get(text=topic_text)
        else:
            topic = Topic(text=topic_text)
            topic.save()

        topic_place = StatisticsTopicPlace(topic=topic, committee=committee)
        topic_place.save()


def reverse_topic_saves(apps, schema_editor):
    Topic = apps.get_model('statisticscore', 'Topic')
    Topic.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('statisticscore', '0038_topics'),
    ]

    operations = [
        migrations.RunPython(save_topics, reverse_topic_saves)
    ]