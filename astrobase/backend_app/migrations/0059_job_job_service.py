# Generated by Django 3.1.13 on 2022-01-02 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0058_auto_20211203_0834'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='job_service',
            field=models.CharField(default='astrobase_services', max_length=30, null=True),
        ),
    ]
