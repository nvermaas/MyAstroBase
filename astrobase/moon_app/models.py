from django.db import models
from django.utils.timezone import datetime

class MoonPhases(models.Model):
    phase = models.CharField(max_length=15)
    date = models.DateField()
    time = models.TimeField

    # there is no database, just a datamodel
    class Meta:
        managed = False