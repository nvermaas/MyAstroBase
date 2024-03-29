# Generated by Django 3.1.13 on 2022-05-11 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('starcharts_app', '0007_auto_20220511_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='starchart',
            name='curve_width',
            field=models.FloatField(default=0.2),
        ),
        migrations.AlterField(
            model_name='starchart',
            name='diagram_size',
            field=models.IntegerField(default=1200),
        ),
        migrations.AlterField(
            model_name='starchart',
            name='display_height',
            field=models.IntegerField(default=800),
        ),
        migrations.AlterField(
            model_name='starchart',
            name='font_size',
            field=models.IntegerField(default=10),
        ),
        migrations.AlterField(
            model_name='starchart',
            name='magnitude_limit',
            field=models.FloatField(default=10),
        ),
    ]
