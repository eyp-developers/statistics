# Generated by Django 2.0.1 on 2018-01-24 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0036_auto_20171223_1209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='announcement_type',
            field=models.CharField(choices=[('alert-success', 'Success'), ('alert-info', 'Info'), ('alert-warning', 'Warning'), ('alert-danger', 'Danger')], default='alert-info', max_length=15),
        ),
        migrations.AlterField(
            model_name='contentpoint',
            name='point_type',
            field=models.CharField(choices=[('P', 'Point'), ('DR', 'Direct Response')], default='P', max_length=5),
        ),
        migrations.AlterField(
            model_name='gender',
            name='gender',
            field=models.CharField(choices=[('F', 'Female'), ('M', 'Male'), ('O', 'Other')], default='F', max_length=1),
        ),
        migrations.AlterField(
            model_name='point',
            name='point_type',
            field=models.CharField(choices=[('P', 'Point'), ('DR', 'Direct Response')], default='P', max_length=5),
        ),
        migrations.AlterField(
            model_name='runningorder',
            name='point_type',
            field=models.CharField(choices=[('P', 'Point'), ('DR', 'Direct Response')], default='P', max_length=5),
        ),
        migrations.AlterField(
            model_name='session',
            name='country',
            field=models.CharField(choices=[('AL', 'Albania'), ('AM', 'Armenia'), ('AT', 'Austria'), ('AZ', 'Azerbaijan'), ('BY', 'Belarus'), ('BE', 'Belgium'), ('BA', 'Bosnia and Herzegovina'), ('HR', 'Croatia'), ('CY', 'Cyprus'), ('CZ', 'Czech Republic'), ('EE', 'Estonia'), ('FI', 'Finland'), ('FR', 'France'), ('GE', 'Georgia'), ('DE', 'Germany'), ('GR', 'Greece'), ('HU', 'Hungary'), ('IE', 'Ireland'), ('IT', 'Italy'), ('XK', 'Kosovo'), ('LV', 'Latvia'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('NL', 'The Netherlands'), ('NO', 'Norway'), ('PL', 'Poland'), ('PT', 'Portugal'), ('RO', 'Romania'), ('RU', 'Russia'), ('RS', 'Serbia'), ('SI', 'Slovenia'), ('SK', 'Slovakia'), ('ES', 'Spain'), ('SE', 'Sweden'), ('CH', 'Switzerland'), ('TR', 'Turkey'), ('UA', 'Ukraine'), ('GB', 'The United Kingdom')], default='AL', max_length=2),
        ),
        migrations.AlterField(
            model_name='session',
            name='end_date',
            field=models.DateTimeField(verbose_name='end date'),
        ),
        migrations.AlterField(
            model_name='session',
            name='gender_enabled',
            field=models.BooleanField(default=False, verbose_name='gender statistics enabled'),
        ),
        migrations.AlterField(
            model_name='session',
            name='has_technical_problems',
            field=models.BooleanField(default=False, verbose_name='session has technical problems'),
        ),
        migrations.AlterField(
            model_name='session',
            name='is_visible',
            field=models.BooleanField(verbose_name='is visible'),
        ),
        migrations.AlterField(
            model_name='session',
            name='picture',
            field=models.ImageField(upload_to='session_pictures/'),
        ),
        migrations.AlterField(
            model_name='session',
            name='session_statistics',
            field=models.CharField(choices=[('S', 'Statistics Only'), ('C', 'Point Content Only'), ('JF', 'Joint Form Statistics'), ('SF', 'Split Form Statistics'), ('R', 'Running Order Statistics'), ('RC', 'Running Order Statistics with Point Content')], default='JF', max_length=5),
        ),
        migrations.AlterField(
            model_name='session',
            name='session_type',
            field=models.CharField(choices=[('IS', 'International Session'), ('IF', 'International Forum'), ('NS', 'National Session'), ('RS', 'Regional Session'), ('SS', 'Small Scale Session'), ('OE', 'Other Event')], default='RS', max_length=3),
        ),
        migrations.AlterField(
            model_name='session',
            name='start_date',
            field=models.DateTimeField(verbose_name='start date'),
        ),
        migrations.AlterField(
            model_name='session',
            name='voting_enabled',
            field=models.BooleanField(default=True, verbose_name='session-wide voting enabled'),
        ),
    ]
