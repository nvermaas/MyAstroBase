# Generated by Django 3.1.13 on 2022-05-14 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('starcharts_app', '0008_auto_20220511_1658'),
    ]

    operations = [
        migrations.AddField(
            model_name='starchart',
            name='background_color',
            field=models.CharField(default='black', max_length=10),
        ),
        migrations.AddField(
            model_name='starchart',
            name='scheme',
            field=models.CharField(default='default', max_length=15),
        ),
    ]
