from django.db import models

class MoonPhases(models.Model):
    phase = models.CharField(max_length=15)
    date = models.DateField()
    time = models.TimeField

    # there is no database, just a datamodel
    class Meta:
        managed = False

class StarChart(models.Model):
    name = models.CharField(default='change me', max_length=15)
    ra_min = models.FloatField()
    ra_max = models.FloatField()
    dec_min = models.FloatField()
    dec_max = models.FloatField()
    magnitude_limit = models.FloatField()

    image = models.ImageField(upload_to='my_starmaps')

