# Generated by Django 2.2.6 on 2019-10-27 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0006_astrofile_new_filename'),
    ]

    operations = [
        migrations.AddField(
            model_name='observation',
            name='description',
            field=models.CharField(default='', max_length=255),
        ),
    ]
