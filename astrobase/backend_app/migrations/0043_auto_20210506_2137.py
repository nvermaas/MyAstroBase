# Generated by Django 3.1.8 on 2021-05-06 19:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0042_auto_20210506_2103'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='observation2',
            name='derived_annotated_grid_eq_image',
        ),
        migrations.RemoveField(
            model_name='observation2',
            name='derived_annotated_grid_image',
        ),
        migrations.RemoveField(
            model_name='observation2',
            name='derived_annotated_image',
        ),
        migrations.RemoveField(
            model_name='observation2',
            name='derived_annotated_stars_image',
        ),
        migrations.RemoveField(
            model_name='observation2',
            name='derived_annotated_transient_image',
        ),
        migrations.RemoveField(
            model_name='observation2',
            name='derived_fits',
        ),
        migrations.RemoveField(
            model_name='observation2',
            name='derived_sky_globe_image',
        ),
        migrations.RemoveField(
            model_name='observation2',
            name='derived_sky_plot_image',
        ),
    ]
