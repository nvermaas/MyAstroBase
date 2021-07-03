from django.conf import settings
from ..models import Exoplanet

def update_exoplanet_table():

    # clear asteroid table
    Exoplanet.objects.all().delete()

    with open(settings.MY_EXOPLANETS_ROOT, "r") as f:
        line = f.readline()

        while line != '':  # The EOF char is an empty string

            # skip comments
            if line.startswith('#'):
                line = f.readline()
                continue

            # also skip header
            if line.startswith('rowid'):
                line = f.readline()
                continue

            list = line.split(',')

            exoplanet = Exoplanet(
                pl_name=list[1],
                hostname=list[2],
                pl_letter= list[3],
                hd_name = list[4],
                hip_name=list[5],
                tic_name=list[6],
                gaia_name=list[7],
                sy_snum=list[9],
                sy_pnum=list[10],
                disc_year=list[14],
                disc_facility=list[18],
                soltype=list[31],
                pl_rade=list[42],
                pl_bmasse=list[50],
                st_spectype=list[154],
                ra=list[202],
                dec=list[204],
                sy_dist=list[218],
                sy_vmag=list[227],
            )

            try:
                exoplanet.save()
                print(list[0], list[1])
            except:
                pass
            line = f.readline()