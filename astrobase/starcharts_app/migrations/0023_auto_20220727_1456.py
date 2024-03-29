# Generated by Django 3.1.13 on 2022-07-27 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('starcharts_app', '0022_auto_20220521_1720'),
    ]

    operations = [
        migrations.AddField(
            model_name='starchart',
            name='query_limit',
            field=models.IntegerField(default=10000),
        ),
        migrations.AddField(
            model_name='starchart',
            name='source',
            field=models.CharField(choices=[('ucac4_postgres', 'ucac4_postgres'), ('hyg_sqlite', 'hyg_sqlite')], default='ucac4_postgres', max_length=30),
        ),
    ]
