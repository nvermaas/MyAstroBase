# Generated by Django 3.1.13 on 2021-11-20 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0056_auto_20211114_1535'),
    ]

    operations = [
        migrations.AddField(
            model_name='cutout',
            name='observation_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cutout',
            name='observation_name',
            field=models.CharField(default='unknown', max_length=40),
        ),
    ]
