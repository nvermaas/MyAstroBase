from django.db import models

# settings.MY_HYG_ROOT
class Stars(models.Model):
    RightAscension = models.FloatField()
    Declination = models.FloatField()

    HipparcosID = models.CharField(max_length=10)
    HenryDraperID = models.CharField(max_length=10)
    BayerFlamsteed = models.CharField(max_length=10)
    DistanceInParsecs = models.FloatField()
    ProperMotionRA = models.FloatField()
    ProperMotionDec = models.FloatField()
    RadialVelocity = models.FloatField()
    Magnitude = models.FloatField()
    AbsoluteMagnitude = models.FloatField()
    Luminosity = models.FloatField()
    SpectralType = models.CharField(max_length=10)
    ColorIndex = models.FloatField()
    Constellation = models.CharField(max_length=5)
    VariableMinimum = models.FloatField()
    VariableMaximum = models.FloatField()

class Scheme(models.Model):
    name = models.CharField(default='default', max_length=30)
    magnitude_limit = models.FloatField(default=10)
    dimmest_mag = models.FloatField(default=8)
    brightest_mag = models.FloatField(default=-1.5)
    min_d = models.IntegerField(default=1)
    max_d = models.IntegerField(default=4)

    font_size = models.IntegerField(default=10)
    font_color = models.CharField(default='#167ac6', max_length=10)

    curve_width = models.FloatField(default=0.2)
    curve_color = models.CharField(default='#FFF', max_length=10)
    star_color = models.CharField(default='#FFF', max_length=10)
    background = models.CharField(default='black', max_length=10)

    def __str__(self):
        return self.name


class StarChart(models.Model):
    name = models.CharField(default='change me', max_length=30)
    ra_min = models.FloatField()
    ra_max = models.FloatField()
    dec_min = models.FloatField()
    dec_max = models.FloatField()
    magnitude_limit = models.FloatField(default=10)
    dimmest_mag = models.FloatField(default=8)
    brightest_mag = models.FloatField(default=-1.5)
    min_d = models.IntegerField(default=1)
    max_d = models.IntegerField(default=4)

    image = models.ImageField(upload_to='my_starmaps')

    diagram_size = models.IntegerField(default=1200)
    display_width = models.IntegerField(default=1200)
    display_height = models.IntegerField(default=800)

    font_size = models.IntegerField(default=10)
    font_color = models.CharField(default='#167ac6', max_length=10)

    curve_width = models.FloatField(default=0.2)
    curve_color = models.CharField(default='#FFF', max_length=10)
    star_color = models.CharField(default='#FFF', max_length=10)
    background = models.CharField(default='black', max_length=10)
    scheme = models.ForeignKey(Scheme, on_delete=models.SET_NULL, null=True, blank=True)
    previous_scheme_name = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        # check if the scheme needs to be applied, overwrite the colors
        apply_scheme = False

        try:
            if (self.previous_scheme_name != self.scheme.name):
                apply_scheme = True

        except:
            pass

        if (apply_scheme):
            self.background = self.scheme.background
            self.star_color = self.scheme.star_color

        try:
            self.previous_scheme_name = self.scheme.name
        except:
            self.previous_scheme_name = None

        # continue the save
        super(StarChart, self).save(*args, **kwargs)
