import numpy as np
#from matplotlib import pyplot as plt
#from matplotlib.collections import LineCollection

from skyfield.api import Star, load
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
from skyfield.data import hipparcos, mpc, stellarium
from skyfield.projections import build_stereographic_projection

# /astrobase/post_dataproducts?taskid=190405001
def create_starmap(command, observation_id):
    url = ''
    return url