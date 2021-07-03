from django.db import models

# Create your models here.
class Exoplanet(models.Model):

    pl_name = models.CharField(verbose_name="Planet Name",max_length=30, unique=True)
    hostname = models.CharField(verbose_name="Host Name",max_length=15,null=True)
    pl_letter = models.CharField(verbose_name="Planet Letter", max_length=2,null=True)
    hd_name = models.CharField(verbose_name="HD ID", max_length=15,null=True)
    hip_name = models.CharField(verbose_name="HIP ID", max_length=15,null=True)
    tic_name = models.CharField(verbose_name="TESS ID", max_length=15,null=True)
    gaia_name = models.CharField(verbose_name="GAIA ID", max_length=30,null=True)
    sy_snum = models.IntegerField(verbose_name="Number of Stars",null=True)
    sy_pnum = models.IntegerField(verbose_name="Number of Planets",null=True)
    disc_year = models.IntegerField(verbose_name="Discovery Year",null=True)
    disc_facility = models.CharField(verbose_name="Discovery Facility", max_length=30,null=True)
    soltype = models.CharField(verbose_name="Solution Type", max_length=30,null=True)
    pl_rade = models.CharField(verbose_name="Planet Radius [Earth Radius]",max_length=30,null=True)
    pl_bmasse = models.CharField(verbose_name="Planet Mass or Mass*sin(i) [Earth Mass]",max_length=30,null=True)
    st_spectype = models.CharField(verbose_name="Spectral Type", max_length=10,null=True)

    ra = models.FloatField(null=True)
    dec = models.FloatField(null=True)
    sy_dist = models.CharField(max_length=15,null=True)
    sy_vmag = models.CharField(max_length=15,null=True)

    def __str__(self):
        return self.pl_name