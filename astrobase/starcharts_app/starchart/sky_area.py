import math

class SkyArea:
    def __init__(self, ra0, ra1, dec0, dec1, mag_min):
        self.ra_min  = min(ra0, ra1)
        self.ra_max  = max(ra0, ra1)
        self.dec_min = min(dec0, dec1)
        self.dec_max = max(dec0, dec1)
        self.mag_min = mag_min

class ConeToSkyArea:
    def __init__(self, ra, dec, radius_ra, radius_dec, mag_min):

        self.dec_min = dec - radius_dec
        self.dec_max = dec + radius_dec
        dec_factor = 1 / math.cos(math.radians(dec))

        self.ra_min = ra - (radius_ra * dec_factor)
        self.ra_max = ra + (radius_ra * dec_factor)
        self.mag_min = mag_min