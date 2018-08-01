# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveDebate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active_debate', models.CharField(max_length=7, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ActiveRound',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active_round', models.PositiveSmallIntegerField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Committee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('committee_name', models.CharField(max_length=7)),
                ('committee_topic', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('active_debate', models.CharField(max_length=7, null=True, blank=True)),
                ('active_round', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('point_type', models.CharField(default=b'P', max_length=5, choices=[(b'P', b'Point'), (b'DR', b'Direct Response')])),
                ('committee_by', models.ForeignKey(on_delete=models.deletion.CASCADE, to='statistics.Committee')),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session_name', models.CharField(max_length=100)),
                ('session_description', models.CharField(max_length=200)),
                ('session_picture', models.URLField()),
                ('session_country', models.CharField(default=b'AL', max_length=2, choices=[(b'AL', b'Albania'), (b'AM', b'Armenia'), (b'AT', b'Austria'), (b'AZ', b'Azerbaijan'), (b'BY', b'Belarus'), (b'BE', b'Belgium'), (b'BA', b'Bosnia and Herzegovina'), (b'HR', b'Croatia'), (b'CY', b'Cyprus'), (b'CZ', b'Czech Republic'), (b'DK', b'Denmark'), (b'EE', b'Estonia'), (b'FI', b'Finland'), (b'FR', b'France'), (b'GE', b'Georgia'), (b'DE', b'Germany'), (b'GR', b'Greece'), (b'HU', b'Hungary'), (b'IE', b'Ireland'), (b'IT', b'Italy'), (b'XK', b'Kosovo'), (b'LV', b'Latvia'), (b'LT', b'Lithuania'), (b'LU', b'Luxembourg'), (b'NL', b'The Netherlands'), (b'NO', b'Norway'), (b'PL', b'Poland'), (b'PT', b'Portugal'), (b'RO', b'Romania'), (b'RU', b'Russia'), (b'RS', b'Serbia'), (b'SI', b'Slovenia'), (b'ES', b'Spain'), (b'SE', b'Sweden'), (b'CH', b'Swizerland'), (b'TR', b'Turkey'), (b'UA', b'Ukraine'), (b'GB', b'The United Kingdom')])),
                ('session_start_date', models.DateTimeField(verbose_name=b'start date')),
                ('session_end_date', models.DateTimeField(verbose_name=b'end date')),
                ('session_rounds_enabled', models.BooleanField(default=True, verbose_name=b'debate rounds enabled')),
                ('session_subtopics_enabled', models.BooleanField(default=True, verbose_name=b'committee subtopics enabled')),
                ('session_voting_enabled', models.BooleanField(default=True, verbose_name=b'session-wide voting enabled')),
                ('session_max_rounds', models.PositiveSmallIntegerField(default=3)),
                ('session_admin_user', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='session_admin', blank=True, to=settings.AUTH_USER_MODEL)),
                ('session_submission_user', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='session_submit', blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SubTopic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subtopic_text', models.CharField(max_length=200, null=True, blank=True)),
                ('committee', models.ForeignKey(on_delete=models.deletion.CASCADE, blank=True, to='statistics.Committee', null=True)),
                ('session', models.ForeignKey(on_delete=models.deletion.CASCADE, blank=True, to='statistics.Session', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now=True, null=True)),
                ('active_debate', models.CharField(max_length=7)),
                ('in_favour', models.PositiveSmallIntegerField()),
                ('against', models.PositiveSmallIntegerField()),
                ('abstentions', models.PositiveSmallIntegerField()),
                ('absent', models.PositiveSmallIntegerField()),
                ('committee_by', models.ForeignKey(on_delete=models.deletion.CASCADE, to='statistics.Committee')),
                ('session', models.ForeignKey(on_delete=models.deletion.CASCADE, to='statistics.Session')),
            ],
        ),
        migrations.AddField(
            model_name='point',
            name='session',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='statistics.Session'),
        ),
        migrations.AddField(
            model_name='point',
            name='subtopics',
            field=models.ManyToManyField(to='statistics.SubTopic', blank=True),
        ),
        migrations.AddField(
            model_name='committee',
            name='session',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='statistics.Session'),
        ),
        migrations.AddField(
            model_name='activeround',
            name='session',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='statistics.Session'),
        ),
        migrations.AddField(
            model_name='activedebate',
            name='session',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='statistics.Session'),
        ),
    ]
