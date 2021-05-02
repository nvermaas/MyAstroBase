from django.db import models
from django.utils.timezone import datetime

class Transient(models.Model):
    phase = models.CharField(max_length=15)
    date = models.DateField()
    time = models.TimeField

    # there is no database, just a datamodel
    class Meta:
        managed = False


class Asteroid(models.Model):
    # static info from minor planet center
    designation = models.CharField(max_length=30)
    absolute_magnitude = models.FloatField(null = True)

    # ephemeris
    timestamp = models.DateTimeField(null = True)
    visual_magnitude = models.FloatField(null = True)
    ra = models.FloatField('ra', null = True)
    dec = models.FloatField('dec', null = True)

    def __str__(self):
        return self.designation