from django.db import models

# Create your models here.
class Exoplanet(models.Model):

    pl_name = models.CharField(verbose_name="Planet Name",max_length=30)
    hostname = models.CharField(verbose_name="Host Name",max_length=30)

    sy_snum = models.IntegerField(verbose_name="Number of Stars")
    sy_pnum = models.IntegerField(verbose_name="Number of Planets")
    disc_year = models.IntegerField(verbose_name="Discovery Year")
    soltype = models.CharField(verbose_name="Solution Type", max_length=30)
    pl_rade = models.FloatField(verbose_name="Planet Radius [Earth Radius]")
    pl_bmasse = models.FloatField(verbose_name="Planet Mass or Mass*sin(i) [Earth Mass]")
    st_spectype = models.CharField(verbose_name="Spectral Type", max_length=30)

    ra = models.FloatField(null = True)
    dec = models.FloatField(null=True)
    sy_dist = models.FloatField(null=True)
    sy_vmag = models.FloatField(null=True)

    def __str__(self):
        return self.pl_name