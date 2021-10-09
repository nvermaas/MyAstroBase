# Generated by Django 2.2.13 on 2020-11-27 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0026_auto_20201118_0807'),
    ]

    operations = [
        migrations.AddField(
            model_name='observation',
            name='dec_max',
            field=models.FloatField(null=True, verbose_name='dec_max'),
        ),
        migrations.AddField(
            model_name='observation',
            name='dec_min',
            field=models.FloatField(null=True, verbose_name='dec_min'),
        ),
        migrations.AddField(
            model_name='observation',
            name='ra_max',
            field=models.FloatField(null=True, verbose_name='ra_max'),
        ),
        migrations.AddField(
            model_name='observation',
            name='ra_min',
            field=models.FloatField(null=True, verbose_name='ra_min'),
        ),
    ]