# Generated by Django 3.1.8 on 2021-05-08 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0045_auto_20210508_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observation2',
            name='annotated_grid_eq_image',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='observation2',
            name='annotated_grid_image',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='observation2',
            name='annotated_stars_image',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='observation2',
            name='annotated_transient_image',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]