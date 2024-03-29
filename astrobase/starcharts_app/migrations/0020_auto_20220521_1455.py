# Generated by Django 3.1.13 on 2022-05-21 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('starcharts_app', '0019_auto_20220515_1950'),
    ]

    operations = [
        migrations.AddField(
            model_name='stars',
            name='AbsoluteMagnitude',
            field=models.FloatField(default=None),
        ),
        migrations.AddField(
            model_name='stars',
            name='ColorIndex',
            field=models.FloatField(default=None),
        ),
        migrations.AddField(
            model_name='stars',
            name='Constellation',
            field=models.CharField(default=None, max_length=5),
        ),
        migrations.AddField(
            model_name='stars',
            name='DistanceInParsecs',
            field=models.FloatField(default=None),
        ),
        migrations.AddField(
            model_name='stars',
            name='Luminosity',
            field=models.FloatField(default=None),
        ),
        migrations.AddField(
            model_name='stars',
            name='ProperMotionDec',
            field=models.FloatField(default=None),
        ),
        migrations.AddField(
            model_name='stars',
            name='ProperMotionRA',
            field=models.FloatField(default=None),
        ),
        migrations.AddField(
            model_name='stars',
            name='RadialVelocity',
            field=models.FloatField(default=None),
        ),
        migrations.AddField(
            model_name='stars',
            name='SpectralType',
            field=models.CharField(default=None, max_length=10),
        ),
        migrations.AddField(
            model_name='stars',
            name='VariableMaximum',
            field=models.FloatField(default=None),
        ),
        migrations.AddField(
            model_name='stars',
            name='VariableMinimum',
            field=models.FloatField(default=None),
        ),
        migrations.AlterField(
            model_name='stars',
            name='BayerFlamsteed',
            field=models.CharField(default=None, max_length=10),
        ),
        migrations.AlterField(
            model_name='stars',
            name='HenryDraperID',
            field=models.CharField(default=None, max_length=10),
        ),
        migrations.AlterField(
            model_name='stars',
            name='HipparcosID',
            field=models.CharField(default=None, max_length=10),
        ),
        migrations.AlterField(
            model_name='stars',
            name='Magnitude',
            field=models.FloatField(default=None),
        ),
    ]
