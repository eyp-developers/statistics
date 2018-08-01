# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0012_auto_20150822_1237'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='session_facebook_link',
            field=models.URLField(default='http://example.com/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='session',
            name='session_resolution_link',
            field=models.URLField(default='http://google.com/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='session',
            name='session_twitter_link',
            field=models.URLField(default='http://google.com/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='session',
            name='session_website_link',
            field=models.URLField(default='http://google.com/'),
            preserve_default=False,
        ),
    ]
