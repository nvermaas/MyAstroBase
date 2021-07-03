# Generated by Django 3.1.8 on 2021-05-08 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0043_auto_20210506_2137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observation2',
            name='annotated_grid_eq_image',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='observation2',
            name='annotated_grid_image',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='observation2',
            name='annotated_image',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='observation2',
            name='annotated_stars_image',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='observation2',
            name='annotated_transient_image',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='observation2',
            name='fits',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='observation2',
            name='sky_globe_image',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='observation2',
            name='sky_plot_image',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
