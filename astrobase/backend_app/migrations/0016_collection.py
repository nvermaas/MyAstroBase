# Generated by Django 2.2.6 on 2020-09-26 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0015_auto_20200924_1646'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='unknown', max_length=100)),
                ('collection_type', models.CharField(choices=[('solar system', 'solar system'), ('stars wide angle', 'stars wide angle'), ('stars zoomed-in', 'stars zoomed-in'), ('deep sky', 'deep sky'), ('moon', 'moon'), ('spacecraft', 'spacecraft'), ('scenery', 'scenery'), ('technical', 'technical'), ('event', 'event'), ('other', 'other')], default='other', max_length=20, null=True)),
                ('description', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('observations', models.ManyToManyField(to='backend_app.Observation')),
            ],
        ),
    ]