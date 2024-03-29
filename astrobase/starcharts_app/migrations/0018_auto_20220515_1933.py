# Generated by Django 3.1.13 on 2022-05-15 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('starcharts_app', '0017_starchart_previous_scheme_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stars',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('RightAscension', models.FloatField()),
                ('Declination', models.FloatField()),
                ('Magnitude', models.FloatField()),
                ('BayerFlamsteed', models.CharField(max_length=10)),
            ],
        ),
        migrations.DeleteModel(
            name='MoonPhases',
        ),
    ]
