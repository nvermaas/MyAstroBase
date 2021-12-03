# Generated by Django 3.1.13 on 2021-11-14 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0055_auto_20211114_1432'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cutout',
            name='cutout_directory',
        ),
        migrations.AlterField(
            model_name='cutout',
            name='directory',
            field=models.CharField(db_index=True, max_length=80, null=True),
        ),
    ]
