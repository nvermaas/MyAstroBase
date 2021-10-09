# Generated by Django 3.1.9 on 2021-07-03 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exoplanets', '0002_auto_20210703_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='exoplanet',
            name='gaia_name',
            field=models.CharField(max_length=30, null=True, verbose_name='GAIA ID'),
        ),
        migrations.AddField(
            model_name='exoplanet',
            name='hd_name',
            field=models.CharField(max_length=30, null=True, verbose_name='HD ID'),
        ),
        migrations.AddField(
            model_name='exoplanet',
            name='hip_name',
            field=models.CharField(max_length=30, null=True, verbose_name='HIP ID'),
        ),
        migrations.AddField(
            model_name='exoplanet',
            name='pl_letter',
            field=models.CharField(max_length=30, null=True, verbose_name='Planet Letter'),
        ),
        migrations.AddField(
            model_name='exoplanet',
            name='tic_name',
            field=models.CharField(max_length=30, null=True, verbose_name='TESS ID'),
        ),
        migrations.AlterField(
            model_name='exoplanet',
            name='hostname',
            field=models.CharField(max_length=30, null=True, verbose_name='Host Name'),
        ),
    ]