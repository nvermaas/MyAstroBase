# Generated by Django 3.1.13 on 2022-05-15 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('starcharts_app', '0015_auto_20220515_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheme',
            name='name',
            field=models.CharField(default='default', max_length=30),
        ),
    ]
