# Generated by Django 3.1.13 on 2022-05-15 09:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('starcharts_app', '0012_scheme'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='starchart',
            name='scheme',
        ),
    ]