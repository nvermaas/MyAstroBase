# Generated by Django 3.1.8 on 2021-05-06 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0041_collection2'),
    ]

    operations = [
        migrations.CreateModel(
            name='Observation2Box',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('backend_app.observation2',),
        ),
        migrations.AddField(
            model_name='observation2',
            name='annotated_grid_eq_image',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='observation2',
            name='annotated_grid_image',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='observation2',
            name='annotated_image',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='observation2',
            name='annotated_stars_image',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='observation2',
            name='annotated_transient_image',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='observation2',
            name='fits',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='observation2',
            name='sky_globe_image',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='observation2',
            name='sky_plot_image',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
