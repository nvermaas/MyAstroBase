# Generated by Django 2.2.6 on 2020-11-14 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0019_command'),
    ]

    operations = [
        migrations.AddField(
            model_name='command',
            name='command_id',
            field=models.CharField(default='unknown', max_length=20),
        ),
        migrations.AlterField(
            model_name='command',
            name='command',
            field=models.CharField(default='', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='command',
            name='parameters',
            field=models.CharField(default='', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='command',
            name='type',
            field=models.CharField(default='', max_length=10, null=True),
        ),
    ]
