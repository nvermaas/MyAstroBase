# Generated by Django 2.2.13 on 2020-12-13 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0031_auto_20201129_1732'),
    ]

    operations = [
        migrations.AddField(
            model_name='observation',
            name='used_in_hips',
            field=models.BooleanField(default=False),
        ),
    ]
