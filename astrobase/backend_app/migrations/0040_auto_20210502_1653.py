# Generated by Django 3.1.8 on 2021-05-02 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0039_observation2'),
    ]

    operations = [
        migrations.AddField(
            model_name='observation2',
            name='derived_annotated_grid_eq_image',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='observation2',
            name='derived_annotated_grid_image',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='observation2',
            name='derived_annotated_image',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='observation2',
            name='derived_annotated_stars_image',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='observation2',
            name='derived_annotated_transient_image',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='observation2',
            name='derived_fits',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='observation2',
            name='derived_sky_globe_image',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='observation2',
            name='derived_sky_plot_image',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
    ]
