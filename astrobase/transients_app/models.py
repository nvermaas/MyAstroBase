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
    designation = models.CharField(max_length=30)

    def __str__(self):
        return self.designation