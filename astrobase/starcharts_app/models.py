from django.db import models

SOURCE_CHOICES = [
    ('ucac4_postgres', 'ucac4_postgres'),
    ('hyg_sqlite', 'hyg_sqlite'),
]

OUTPUT_CHOICES = [
    ('svg', 'svg'),
    ('png', 'png'),
]

LABEL_CHOICES = [
    ('HipparcosID', 'HipparcosID'),
    ('HenryDraperID', 'HenryDraperID'),
    ('GlieseID', 'GlieseID'),
    ('BayerFlamsteed', 'BayerFlamsteed'),
    ('ProperName', 'ProperName')
]

# settings.MY_HYG_ROOT
class Stars(models.Model):
    RightAscension = models.FloatField()
    Declination = models.FloatField()

    HipparcosID = models.CharField(max_length=10, default=None, null=True)
    HenryDraperID = models.CharField(max_length=10, default=None, null=True)
    BayerFlamsteed = models.CharField(max_length=10, default=None, null=True)
    GlieseID = models.CharField(max_length=10, default=None, null=True)
    DistanceInParsecs = models.FloatField(default=None, null=True)
    ProperMotionRA = models.FloatField(default=None, null=True)
    ProperMotionDec = models.FloatField(default=None, null=True)
    RadialVelocity = models.FloatField(default=None, null=True)
    Magnitude = models.FloatField(default=None, null=True)
    AbsoluteMagnitude = models.FloatField(default=None, null=True)
    Luminosity = models.FloatField(default=None, null=True)
    SpectralType = models.CharField(max_length=10, default=None, null=True)
    ColorIndex = models.FloatField(default=None, null=True)
    Constellation = models.CharField(max_length=5, default=None, null=True)
    VariableMinimum = models.FloatField(default=None, null=True)
    VariableMaximum = models.FloatField(default=None, null=True)

    def __str__(self):
        return str(self.id) + "(" + str(self.HipparcosID) + str(self.GlieseID) +")"

class Scheme(models.Model):
    name = models.CharField(default='default', max_length=30)
    source = models.CharField(choices=SOURCE_CHOICES, default='ucac4_postgres', max_length=30)
    output_format = models.CharField(choices=OUTPUT_CHOICES, default='svg', max_length=3)
    label_field = models.CharField(choices=LABEL_CHOICES, default='BayerFlamsteed', max_length=15)
    query_limit = models.IntegerField(default=10000)

    magnitude_limit = models.FloatField(default=7)
    dimmest_mag = models.FloatField(default=6)
    brightest_mag = models.FloatField(default=-1.5)
    min_d = models.IntegerField(default=1)
    max_d = models.IntegerField(default=4)

    diagram_size = models.IntegerField(default=800)
    display_width = models.IntegerField(default=800)
    display_height = models.IntegerField(default=600)
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
    source = models.CharField(choices=SOURCE_CHOICES, default='ucac4_postgres', max_length=30)
    output_format = models.CharField(choices=OUTPUT_CHOICES, default='svg', max_length=3)
    label_field = models.CharField(choices=LABEL_CHOICES, default='BayerFlamsteed', max_length=15)
    query_limit = models.IntegerField(default=10000)
    nr_of_stars = models.IntegerField(default=0)

    ra = models.FloatField(null=True)
    dec = models.FloatField(null=True)
    radius_ra = models.FloatField(null=True)
    radius_dec = models.FloatField(null=True)

    ra_min = models.FloatField(null=True)
    ra_max = models.FloatField(null=True)
    dec_min = models.FloatField(null=True)
    dec_max = models.FloatField(null=True)

    rotation = models.FloatField(default=0)
    magnitude_limit = models.FloatField(default=10)
    dimmest_mag = models.FloatField(default=9)
    brightest_mag = models.FloatField(default=-2)
    min_d = models.IntegerField(default=1)
    max_d = models.IntegerField(default=6)

    image = models.ImageField(upload_to='my_starmaps')

    diagram_size = models.IntegerField(default=800)
    display_width = models.IntegerField(default=800)
    display_height = models.IntegerField(default=600)

    font_size = models.IntegerField(default=15)
    #font_color = models.CharField(default='#167ac6', max_length=10)
    font_color = models.CharField(default='yellow', max_length=10)

    curve_width = models.FloatField(default=0.2)
    curve_color = models.CharField(default='#FFF', max_length=10)
    star_color = models.CharField(default='#FFF', max_length=10)
    background = models.CharField(default='black', max_length=10)
    scheme = models.ForeignKey(Scheme, on_delete=models.SET_NULL, null=True, blank=True)
    previous_scheme_name = models.CharField(max_length=30, null=True, blank=True)
    extra = models.TextField(null=True, blank=True)

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
