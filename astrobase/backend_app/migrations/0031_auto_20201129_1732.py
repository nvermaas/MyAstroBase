# Generated by Django 2.2.13 on 2020-11-29 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0030_auto_20201129_1713'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskobject',
            name='astrometry_url',
            field=models.CharField(blank=True, default='http://nova.astrometry.net', max_length=50, null=True),
        ),
    ]
