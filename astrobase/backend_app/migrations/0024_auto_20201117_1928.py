# Generated by Django 2.2.13 on 2020-11-17 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0023_auto_20201117_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='type',
            field=models.CharField(default='', max_length=50, null=True),
        ),
    ]