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
    magnitude_limit = models.FloatField(default=10)
    dimmest_mag = models.FloatField(default=8)
    brightest_mag = models.FloatField(default=-1.5)
    min_diameter = models.IntegerField(default=1)
    max_diameter = models.IntegerField(default=4)

    image = models.ImageField(upload_to='my_starmaps')

    diagram_size = models.IntegerField(default=1200)
    display_width = models.IntegerField(default=1200)
    display_height = models.IntegerField(default=800)

    font_size = models.IntegerField(default=10)
    font_color = models.CharField(default='#167ac6', max_length=10)

    curve_width = models.FloatField(default=0.2)
    curve_color = models.CharField(default='#FFF', max_length=10)
    star_color = models.CharField(default='#FFF', max_length=10)

    def __str__(self):
        return self.name