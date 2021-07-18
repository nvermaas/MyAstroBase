# Generated by Django 3.1.9 on 2021-07-18 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0046_auto_20210508_1318'),
    ]

    operations = [
        migrations.AddField(
            model_name='observation2',
            name='annotated_exoplanets_image',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='observation2',
            name='filter',
            field=models.CharField(choices=[('None', 'None'), ('CLS', 'CLS'), ('other', 'other')], default='CLS', max_length=50),
        ),
        migrations.AlterField(
            model_name='observation2',
            name='instrument',
            field=models.CharField(choices=[('Powershot G2', 'Powershot G2'), ('Powershot G15', 'Powershot G15'), ('Canon 350D', 'Canon 350D'), ('Canon 2000D', 'Canon 2000D'), ('other', 'other')], default='Canon 2000D', max_length=50),
        ),
    ]
