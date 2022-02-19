# Generated by Django 2.0.1 on 2018-07-25 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statisticscore', '0043_merge_20180207_1821'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='topic_overview_link',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='historictopicplace',
            name='historic_country',
            field=models.CharField(blank=True, choices=[('AL', 'Albania'), ('AM', 'Armenia'), ('AT', 'Austria'), ('AZ', 'Azerbaijan'), ('BY', 'Belarus'), ('BE', 'Belgium'), ('BA', 'Bosnia and Herzegovina'), ('HR', 'Croatia'), ('CY', 'Cyprus'), ('CZ', 'Czech Republic'), ('DK', 'Denmark'), ('EE', 'Estonia'), ('FI', 'Finland'), ('FR', 'France'), ('GE', 'Georgia'), ('DE', 'Germany'), ('GR', 'Greece'), ('HU', 'Hungary'), ('IE', 'Ireland'), ('IT', 'Italy'), ('XK', 'Kosovo'), ('LV', 'Latvia'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('NL', 'The Netherlands'), ('NO', 'Norway'), ('PL', 'Poland'), ('PT', 'Portugal'), ('RO', 'Romania'), ('RU', 'Russia'), ('RS', 'Serbia'), ('SI', 'Slovenia'), ('SK', 'Slovakia'), ('ES', 'Spain'), ('SE', 'Sweden'), ('CH', 'Switzerland'), ('TR', 'Turkey'), ('UA', 'Ukraine'), ('GB', 'The United Kingdom')], max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='historictopicplace',
            name='historic_session_type',
            field=models.CharField(blank=True, choices=[('IS', 'International Session'), ('IF', 'International Forum'), ('NS', 'National Session'), ('RS', 'Regional Session'), ('SS', 'Small Scale Session'), ('OE', 'Other Event')], max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='topic',
            name='difficulty',
            field=models.CharField(blank=True, choices=[('E', 'Easy'), ('I', 'Intermediate'), ('H', 'Hard')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='topic',
            name='type',
            field=models.CharField(blank=True, choices=[('CR', 'Creative'), ('CF', 'Conflict'), ('ST', 'Strategy')], max_length=2, null=True),
        ),
    ]
