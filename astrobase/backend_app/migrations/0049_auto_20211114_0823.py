# Generated by Django 3.1.13 on 2021-11-14 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0048_auto_20211114_0815'),
    ]

    operations = [
        migrations.AddField(
            model_name='cutout',
            name='status',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='cutout',
            name='quality',
            field=models.CharField(default='good', max_length=15, null=True),
        ),
    ]
