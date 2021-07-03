# Generated by Django 3.1.9 on 2021-07-03 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exoplanets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exoplanet',
            name='disc_year',
            field=models.IntegerField(null=True, verbose_name='Discovery Year'),
        ),
        migrations.AlterField(
            model_name='exoplanet',
            name='pl_bmasse',
            field=models.FloatField(null=True, verbose_name='Planet Mass or Mass*sin(i) [Earth Mass]'),
        ),
        migrations.AlterField(
            model_name='exoplanet',
            name='pl_rade',
            field=models.FloatField(null=True, verbose_name='Planet Radius [Earth Radius]'),
        ),
        migrations.AlterField(
            model_name='exoplanet',
            name='soltype',
            field=models.CharField(max_length=30, null=True, verbose_name='Solution Type'),
        ),
        migrations.AlterField(
            model_name='exoplanet',
            name='st_spectype',
            field=models.CharField(max_length=30, null=True, verbose_name='Spectral Type'),
        ),
        migrations.AlterField(
            model_name='exoplanet',
            name='sy_pnum',
            field=models.IntegerField(null=True, verbose_name='Number of Planets'),
        ),
        migrations.AlterField(
            model_name='exoplanet',
            name='sy_snum',
            field=models.IntegerField(null=True, verbose_name='Number of Stars'),
        ),
    ]
