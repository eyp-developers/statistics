# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-11-10 15:25


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statisticscore', '0034_remove_session_session_color'),
    ]

    operations = [
        migrations.RenameField(
            model_name='announcement',
            old_name='announcement_content',
            new_name='content',
        ),
        migrations.RenameField(
            model_name='announcement',
            old_name='announcement_timestamp',
            new_name='timestamp',
        ),
        migrations.RenameField(
            model_name='announcement',
            old_name='announcement_valid_until',
            new_name='valid_until',
        ),
        migrations.RenameField(
            model_name='committee',
            old_name='committee_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='committee',
            old_name='committee_topic',
            new_name='topic',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_admin_user',
            new_name='admin_user',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_country',
            new_name='country',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_description',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_email',
            new_name='email',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_end_date',
            new_name='end_date',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_facebook_link',
            new_name='facebook_link',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_gender_enabled',
            new_name='gender_enabled',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_has_technical_problems',
            new_name='has_technical_problems',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_is_visible',
            new_name='is_visible',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_max_rounds',
            new_name='max_rounds',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_picture_author_link',
            new_name='picture_author_link',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_picture_license_link',
            new_name='picture_license_link',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_resolution_link',
            new_name='resolution_link',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_start_date',
            new_name='start_date',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_submission_user',
            new_name='submission_user',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_twitter_link',
            new_name='twitter_link',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_voting_enabled',
            new_name='voting_enabled',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_website_link',
            new_name='website_link',
        ),
        migrations.RenameField(
            model_name='subtopic',
            old_name='subtopic_text',
            new_name='text',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_picture',
            new_name='picture',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_picture_author',
            new_name='picture_author',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='session_picture_license',
            new_name='picture_licence',
        ),
    ]
