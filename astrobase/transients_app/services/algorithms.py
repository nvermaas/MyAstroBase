import requests
import math
import datetime
from django.conf import settings

import numpy as np

from skyfield.api import load
from skyfield.data import mpc
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN

try:
    import ephem
except:
    pass

from ..models import Asteroid

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%Y-%m-%d %H:%M:%SZ"
DJANGO_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def phi_func(index, phase_angle):
    """
    Phase function that is needed for the reduced magnitude. The function has
    two versions, depending on the index ('1' or '2').
    Parameters
    ----------
    index : str
        Phase function index / version. '1' or '2'.
    phase_angle : float
        Phase angle of the asteroid in radians.
    Returns
    -------
    phi : float
        Phase function result.
    """

    # Dictionary that contains the A and B constants, depending on the index /
    # version
    a_factor = {'1': 3.33, \
                '2': 1.87}

    b_factor = {'1': 0.63, \
                '2': 1.22}

    # Phase function
    phi = np.exp(-1.0 * a_factor[index] \
                 *+ ((np.tan(0.5 * phase_angle) ** b_factor[index])))

    # Return the phase function result
    return phi


def red_mag(abs_mag, phase_angle, slope_g):
    """
    Reduced magnitude of an asteroid, depending on the absolute magnitude,
    phase angle and slope parameter (G)
    Parameters
    ----------
    abs_mag : float
        Absolute magnitude.
    phase_angle : float
        Phase angle in radians.
    slope_g : float
        Slope parameter (G), between 0 and 1.
    Returns
    -------
    r_mag : float
        Reduced magnitude.
    """

    # Computation of the reduced magnitude
    r_mag = abs_mag - 2.5 * np.log10((1.0 - slope_g) \
                                     * phi_func(index='1', \
                                                phase_angle=phase_angle) \
                                     + slope_g \
                                     * phi_func(index='2', \
                                                phase_angle=phase_angle))

    # Return the reduced magnitude
    return r_mag

def app_mag(abs_mag, phase_angle, slope_g, d_ast_sun, d_ast_earth):
    """
    Apparent / Visual magnitude of an asteroid (not considering atmospheric
    attenuation), depending on the absolute magnitude, phase angle, the slope
    parameter (G) as well as the distance between the asteroid and Earth,
    respectively the Sun
    Parameters
    ----------
    abs_mag : float
        Absolute magnitude.
    phase_angle : float
        Phase angle in radians.
    slope_g : float
        Slope parameter (G).
    d_ast_sun : float
        Distance between the asteroid and the Sun in AU.
    d_ast_earth : float
        Distance between the asteroid and the Earth in AU.
    Returns
    -------
    mag : float
        Apparent / visual magnitude.
    """

    # Compute the apparent / visual magnitude
    mag = red_mag(abs_mag, phase_angle, slope_g) \
          + 5.0 * np.log10(d_ast_sun * d_ast_earth)

    # Return the apparent magnitude
    return mag


# fetch properties of the orbits of a minor planet by name
def get_minor_planets_webservice(name, timestamp):
    result = {}
    ephemeris = {}

    url = 'https://minorplanetcenter.net/web_service/search_orbits'

    params = {}
    params['name'] = name
    params['json'] = 1

    r = requests.get(url, params, auth=('mpc_ws', 'mpc!!ws'))
    orbital_elements = r.json()
    d = orbital_elements[0]

    # gather the correct orbital elements for the ephem.readdb function
    # http://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId468501
    inclination = d['inclination']
    long_asc_node = d['ascending_node']
    field1 = name
    field2 = 'e' # heliocentric elliptical
    field3 = d['inclination']
    field4 = d['ascending_node']
    field5 = d['argument_of_perihelion']
    field6 = d['semimajor_axis']
    field7 = d['mean_daily_motion']
    field8 = d['eccentricity']
    field9 = d['mean_anomaly']

    # convert "epoch": "2020-12-17.0", to "12/17/2020"
    epoch = datetime.datetime.strptime(d['epoch'], '%Y-%m-%d.0')
    field10 = epoch.strftime("%m/%d/%Y")

    field11 = d['last_opposition_used']
    field12 = "g "+d['absolute_magnitude']
    field13 = "3"
    field14 = "1"
    line = field1 + ',' + field2 + ',' + field3 + ',' + field4 + ',' + field5 + ',' + field6 + ',' + field7 + ',' + \
           field8 + ',' + field9 + ',' + field10 + ',' +field11 + ',' + field12 + ',' + field13 + ',' + field14

    try:
        # todo: replalce ephem with something else (skyfield?) because gcc won't work
        # see how that works for comets

        yh = ephem.readdb(line)

        # convert timestamp to proper observing time for ephem to understand
        observing_time = timestamp.strftime('%Y/%m/%d %H:%M:%S')
        yh.compute(observing_time)

        print(yh.name)
        print("%s %s" % (yh.ra, yh.dec))
        print("%s %s" % (ephem.constellation(yh), yh.mag))

        ephemeris['name'] = yh.name
        ephemeris['timestamp'] = observing_time
        ephemeris['ra'] = str(yh.ra)
        ephemeris['dec'] = str(yh.dec)
        ephemeris['magnitude'] = str(yh.mag)
        ephemeris['constellation'] = str(ephem.constellation(yh))
    except:
        pass

    result['orbital_elements'] = orbital_elements
    result['ephemeris'] = ephemeris

    # https://astroquery.readthedocs.io/en/latest/mpc/mpc.html

    return result


# fetch properties of the orbits of a minor planet by name
def get_transients(name):

    result = {}
    result['name'] = name

    return result


# fetch properties of the orbits of a comet by name and timestamp
# get_comet?name=C/2020 F3 (NEOWISE)&timestamp=2020-07-12T08:55:59Z

def get_comet(name, timestamp):
    # https://rhodesmill.org/skyfield/example-plots.html#drawing-a-finder-chart-for-comet-neowise
    # https://astroquery.readthedocs.io/en/latest/mpc/mpc.html

    # name = "C/2020 F3 (NEOWISE)"
    # https://www.minorplanetcenter.net/iau/info/CometOrbitFormat.html
    with load.open(mpc.COMET_URL) as f:
        comets = mpc.load_comets_dataframe(f)

    comets = (comets.sort_values('reference')
              .groupby('designation', as_index=False).last()
              .set_index('designation', drop=False))

    row = comets.loc[name]
    print(row)
    ts = load.timescale()
    eph = load('de421.bsp')
    sun, earth = eph['sun'], eph['earth']

    comet = sun + mpc.comet_orbit(row, ts, GM_SUN)

    t = ts.utc(timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute)
    ra, dec, distance = earth.at(t).observe(comet).radec()

    result = {}
    result['name'] = name
    result['designation'] = row['designation']
    result['timestamp'] = str(timestamp)
    result['ra'] = str(ra)
    result['dec'] = str(dec)
    result['ra_decimal'] = str(ra.hours * 15)
    result['dec_decimal'] = str(dec.degrees)
    result['distance'] = str(distance)
    result['magnitude_g'] = row['magnitude_g']
    result['magnitude_k'] = row['magnitude_k']
    result['visual_magnitude'] = row['magnitude_k']
    result['row'] = row
    return result,comet


def get_asteroid(name, timestamp):
    # https://rhodesmill.org/skyfield/example-plots.html#drawing-a-finder-chart-for-comet-neowise
    # https://astroquery.readthedocs.io/en/latest/mpc/mpc.html
    designation = name
    try:
        asteroids = Asteroid.objects.filter(designation__icontains=name)
        designation = asteroids[0].designation
    except:
        pass

    with load.open(settings.MY_ASTEROIDS_URL) as f:
        minor_planets = mpc.load_mpcorb_dataframe(f)

    bad_orbits = minor_planets.semimajor_axis_au.isnull()
    minor_planets = minor_planets[~bad_orbits]

    # Index by designation for fast lookup.
    minor_planets = minor_planets.set_index('designation', drop=False)
    row = minor_planets.loc[designation]

    ts = load.timescale()
    eph = load('de421.bsp')
    sun, earth = eph['sun'], eph['earth']

    asteroid = sun + mpc.mpcorb_orbit(row, ts, GM_SUN)
    t = ts.utc(timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute)
    ra, dec, distance_from_sun = sun.at(t).observe(asteroid).radec()
    ra, dec, distance_from_earth = earth.at(t).observe(asteroid).radec()

    # https://towardsdatascience.com/space-science-with-python-a-very-bright-opposition-62e248abfe62
    # how do I calculate the current phase_angle between sun and earth as seen from the asteroid
    ra_sun, dec_sun, d = asteroid.at(t).observe(sun).radec()
    ra_earth,dec_earth, d = asteroid.at(t).observe(earth).radec()

    phase_angle_in_degrees = abs(ra_sun.hours - ra_earth.hours)
    phase_angle = phase_angle_in_degrees * math.pi / 180

    visual_magnitude = app_mag(abs_mag=row['magnitude_H'], \
                             phase_angle=phase_angle, \
                             slope_g=row['magnitude_G'], \
                             d_ast_sun=distance_from_sun.au, \
                             d_ast_earth=distance_from_earth.au)

    result = {}
    result['name'] = name
    result['designation'] = designation
    result['timestamp'] = str(timestamp)
    result['ra'] = str(ra)
    result['dec'] = str(dec)
    result['ra_decimal'] = str(ra.hours * 15)
    result['dec_decimal'] = str(dec.degrees)
    result['distance_from_earth'] = str(distance_from_earth.au)
    result['distance_from_sun'] = str(distance_from_sun.au)
    result['magnitude_h'] = row['magnitude_H']
    result['magnitude_g'] = row['magnitude_G']
    result['visual_magnitude'] = visual_magnitude
    result['last_observation_date'] = row['last_observation_date']
    # result['row'] = row
    return result,asteroid


def update_asteroid_table():

    # clear asteroid table
    Asteroid.objects.all().delete()

#    for b in urllib.request.urlopen(MY_ASTEROID_URL):
#        line = b.decode('utf-8')

    with open(settings.MY_ASTEROIDS_ROOT, "r") as f:
        line = f.readline()

        while line != '':  # The EOF char is an empty string

            # find the absolute magnitude
            m = line[8:13]
            absolute_magnitude = float(m)

            # find the designation
            pos = line.find('(')
            designation = line[pos:pos+20].rstrip()

            asteroid = Asteroid(designation=designation, absolute_magnitude=absolute_magnitude)
            print(designation,absolute_magnitude)
            asteroid.save()

            line = f.readline()


# update the ra,dec and timestamp in the asteroid table
# so that the table can be used to know where asteroids are for a given timestamp
# this function could be executed daily by a service to keep the ra,dec uptodate
def update_asteroid_table_ephemeris(timestamp):

    asteroids = Asteroid.objects.all()

    for asteroid in asteroids:
        designation = asteroid.designation

        details,_ = get_asteroid(designation,timestamp)

        asteroid.ra = details['ra_decimal']
        asteroid.dec = details['dec_decimal']
        asteroid.visual_magnitude = details['visual_magnitude']
        asteroid.timestamp = timestamp
        print(designation)
        asteroid.save()