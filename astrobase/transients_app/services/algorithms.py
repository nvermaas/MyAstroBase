import requests
import math
import datetime
from django.conf import settings

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

MY_ASTEROID_URL = "https://uilennest.net/repository/asteroids.txt"

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

    t = ts.utc(timestamp.year, timestamp.month, timestamp.day)
    ra, dec, distance = earth.at(t).observe(comet).radec()

    result = {}
    result['name'] = name
    result['timestamp'] = str(timestamp)
    result['ra'] = str(ra)
    result['dec'] = str(dec)
    result['ra_decimal'] = str(ra.hours)
    result['dec_decimal'] = str(dec.degrees)
    result['distance'] = str(distance)
    result['magnitude_g'] = row['magnitude_g']
    result['magnitude_k'] = row['magnitude_k']
    result['row'] = row
    return result


def get_asteroid(name, timestamp):
    # https://rhodesmill.org/skyfield/example-plots.html#drawing-a-finder-chart-for-comet-neowise
    # https://astroquery.readthedocs.io/en/latest/mpc/mpc.html
    designation = name
    try:
        asteroids = Asteroid.objects.filter(designation__icontains=name)
        designation = asteroids[0].designation
    except:
        pass

    with load.open(MY_ASTEROID_URL) as f:
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

    # m = g + 5 log rD
    visual_magnitude = row['magnitude_H'] + 5 * math.log(distance_from_sun.au * distance_from_earth.au)

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
    return result


def update_asteroid_table():

    # parse asteroids.txt
    asteroids_file = settings.MY_ASTEROIDS

    # clear asteroid table
    Asteroid.objects.all().delete()

#    for b in urllib.request.urlopen(MY_ASTEROID_URL):
#        line = b.decode('utf-8')

    with open(asteroids_file, "r") as f:
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

        details = get_asteroid(designation,timestamp)

        asteroid.ra = details['ra_decimal']
        asteroid.dec = details['dec_decimal']
        asteroid.visual_magnitude = details['visual_magnitude']
        asteroid.timestamp = timestamp

        asteroid.save()