# Generated by Django 3.1.13 on 2022-08-07 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('starcharts_app', '0026_auto_20220806_1929'),
    ]

    operations = [
        migrations.AddField(
            model_name='starchart',
            name='extra',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='starchart',
            name='output_format',
            field=models.CharField(choices=[('svg', 'svg'), ('png', 'png')], default='svg', max_length=3),
        ),
        migrations.AlterField(
            model_name='starchart',
            name='font_color',
            field=models.CharField(default='yellow', max_length=10),
        ),
        migrations.AlterField(
            model_name='starchart',
            name='font_size',
            field=models.IntegerField(default=15),
        ),
    ]
