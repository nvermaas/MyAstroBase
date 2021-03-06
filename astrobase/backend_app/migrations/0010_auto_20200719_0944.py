# Generated by Django 2.2.6 on 2020-07-19 07:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0009_auto_20191123_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observation',
            name='date',
            field=models.DateTimeField(null=True, verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='observation',
            name='field_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='observation',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='backend_app.Observation'),
        ),
        migrations.AlterField(
            model_name='observation',
            name='process_type',
            field=models.CharField(choices=[('observation', 'observation'), ('pipeline', 'pipeline')], default='observation', max_length=50),
        ),
        migrations.AlterField(
            model_name='taskobject',
            name='task_type',
            field=models.CharField(choices=[('master', 'master'), ('observation', 'observation'), ('dataproduct', 'dataproduct')], default='dataproduct', max_length=20),
        ),
    ]
