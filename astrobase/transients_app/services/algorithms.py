import os
import requests
import math
import json
import datetime
from django.conf import settings

import numpy as np

from skyfield.api import load
from skyfield.data import mpc
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
from skyfield.magnitudelib import planetary_magnitude

try:
    import ephem
except:
    pass

from ..models import Asteroid
from exoplanets.models import Exoplanet

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



def get_comet(name, timestamp):
    # fetch properties of the orbits of a comet by name and timestamp
    # get_comet?name=C/2020 F3 (NEOWISE)&timestamp=2020-07-12T08:55:59Z

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


# http://localhost:8000/my_astrobase/planet/?name=Jupiter
def get_planet(name, timestamp):
    """
    @input name: planet name
    @input timestamp: timestamp to calculate ephemerides with
    @output dict with results
    """

    # https://rhodesmill.org/skyfield/api.html#planetary-magnitudes

    ts = load.timescale()
    eph = load('de421.bsp')
    sun, earth = eph['sun'], eph['earth']
    planet = eph[name+' BARYCENTER']

    t = ts.utc(timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute)
    ra, dec, distance_from_sun = sun.at(t).observe(planet).radec()
    ra, dec, distance_from_earth = earth.at(t).observe(planet).radec()

    # https://towardsdatascience.com/space-science-with-python-a-very-bright-opposition-62e248abfe62
    # how do I calculate the current phase_angle between sun and earth as seen from the asteroid
    ra_sun, dec_sun, d = planet.at(t).observe(sun).radec()
    ra_earth,dec_earth, d = planet.at(t).observe(earth).radec()

    phase_angle_in_degrees = abs(ra_sun.hours - ra_earth.hours)
    phase_angle = phase_angle_in_degrees * math.pi / 180

    eph_planet = eph['earth'].at(t).observe(planet)
    try:
        visual_magnitude = planetary_magnitude(eph_planet)
    except:
        visual_magnitude = 0

    result = {}
    result['name'] = name
    result['designation'] = name
    result['timestamp'] = str(timestamp)
    result['ra'] = str(ra)
    result['dec'] = str(dec)
    result['ra_decimal'] = str(ra.hours * 15)
    result['dec_decimal'] = str(dec.degrees)
    result['distance_from_earth'] = str(distance_from_earth.au)
    result['distance_from_sun'] = str(distance_from_sun.au)
    result['phase_angle'] = phase_angle_in_degrees
    result['visual_magnitude'] = visual_magnitude

    # result['row'] = row
    return result,planet

# http://localhost:8000/my_astrobase/bright_moon/?name=Triton
def get_bright_moon(name, timestamp):
    # https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/a_old_versions/
    eph = load(os.path.join(settings.REPOSITORY_ROOT,'de421.bsp'))        # planets + Earth's Moon
    jup_moons = load(os.path.join(settings.REPOSITORY_ROOT, 'jup365.bsp'))  # Galilean moons
    sat_moons = load(os.path.join(settings.REPOSITORY_ROOT, 'sat365.bsp'))  # Titan, Rhea, Dione, etc.
    ura_moons = load(os.path.join(settings.REPOSITORY_ROOT, 'ura083.bsp'))  # Titania, Oberon
    nep_moons = load(os.path.join(settings.REPOSITORY_ROOT, 'nep076.bsp'))  # Triton

    # Dictionary mapping names → kernel
    MOON_KERNELS = {
        # Jupiter
        "Io": jup_moons,
        "Europa": jup_moons,
        "Ganymede": jup_moons,
        "Callisto": jup_moons,
        # Saturn
        "Titan": sat_moons,
        "Rhea": sat_moons,
        "Dione": sat_moons,
        "Tethys": sat_moons,
        "Iapetus": sat_moons,
        "Enceladus": sat_moons,
        # Uranus
        "Titania": ura_moons,
        "Oberon": ura_moons,
        # Neptune
        "Triton": nep_moons,
    }

    MOON_MAGNITUDES = {
        "Io": 5.0, "Europa": 5.3, "Ganymede": 4.6, "Callisto": 5.6,
        "Titan": 8.4, "Rhea": 9.7, "Dione": 10.4, "Tethys": 10.2,
        "Iapetus": 10.2, "Enceladus": 11.7,
        "Titania": 13.9, "Oberon": 14.1,
        "Triton": 13.5,
        "Phobos": 11.3, "Deimos": 12.4,
    }

    ts = load.timescale()
    sun, earth = eph['sun'], eph['earth']

    # Find the correct kernel
    kernel = MOON_KERNELS.get(name)
    if kernel is None:
        raise ValueError(f"{name} is not in the list of supported bright moons")

    target = kernel[name]

    # Convert timestamp
    t = ts.utc(timestamp.year, timestamp.month, timestamp.day,
               timestamp.hour, timestamp.minute)

    # RA/Dec from Earth
    ra, dec, distance = earth.at(t).observe(target).radec()

    # Phase angle (Sun–Earth as seen from moon)
    ra_sun, dec_sun, _ = target.at(t).observe(sun).radec()
    ra_earth, dec_earth, _ = target.at(t).observe(earth).radec()
    phase_angle_deg = abs(ra_sun.hours - ra_earth.hours)

    result = {
        'name': name,
        'designation': name,
        'timestamp': str(timestamp),
        'ra': str(ra),
        'dec': str(dec),
        'ra_decimal': ra.hours * 15,
        'dec_decimal': dec.degrees,
        'distance_from_earth_au': distance.au,
        'phase_angle_deg': phase_angle_deg,
        'visual_magnitude' : MOON_MAGNITUDES.get(name, None)
    }
    return result, target

# http://localhost:8000/my_astrobase/run-command?command=transient&observation_id=1305
def get_transients_as_json(transient, date):
    transient_list = transient.split(',')

    timestamps = []
    timestamp = date
    midnight = timestamp.replace(hour=0, minute=0, second=0)
    yesterday = midnight + datetime.timedelta(days=-1)
    tomorrow = midnight + datetime.timedelta(days=+1)
    tomorrow2 = midnight + datetime.timedelta(days=+2)
    tomorrow3 = midnight + datetime.timedelta(days=+3)

    timestamps.append(timestamp)
    timestamps.append(midnight)
    timestamps.append(yesterday)
    timestamps.append(tomorrow)
    timestamps.append(tomorrow2)
    timestamps.append(tomorrow3)

    list = []

    for transient_name in transient_list:
        is_bright_moon = False
        count = 0
        for t in timestamps:
            count += 1

            # first try if the transient is a bright moon
            try:
                result, _ = get_bright_moon(transient_name, t)
                is_bright_moon = True

            except:
                # then try a comet
                try:
                    result, _ = get_comet(transient_name, t)
                except:
                    # then try an asteroid
                    try:
                        result, _ = get_asteroid(transient_name, t)
                    except:
                        # finally try a planet
                        result, _ = get_planet(transient_name, t)

            try:
                vmag = round(float(result['visual_magnitude']) * 10) / 10
            except:
                # yikes
                vmag = 0

            if vmag == 0:
                designation = result['designation']
            else:
                designation = result['designation'] + ' (' + str(vmag) + ')'

            line = {}

            if count == 1:
                line['ra'] = float(result['ra_decimal'])
                line['dec'] = float(result['dec_decimal'])
                if is_bright_moon:
                    line['label'] = designation
                    line['shape'] = 'circle_outline'
                    line['size'] = -20
                    line['color'] = 'yellow'
                else:
                    line['label'] = designation
                    line['shape'] = 'circle_outline'
                    line['size'] = -50
                    line['color'] = 'yellow'
                list.append(line)

            else:
                # when it is not a moon, then it makes sense to plot its further course
                if not is_bright_moon:
                    line['ra'] = float(result['ra_decimal'])
                    line['dec'] = float(result['dec_decimal'])
                    line['label'] = str(t.day)
                    line['shape'] = 'cross'
                    line['size'] = vmag
                    line['color'] = 'red'
                    list.append(line)

    extra = json.dumps(list)
    return extra


def get_exoplanets_as_json(observation):
    # roughly cut out the coordinate box of the image, but take a wide margin
    box = observation.box.split(',')
    ra_end = float(box[0]) + 5
    dec_end = float(box[1]) + 5
    ra_start = float(box[4]) - 5
    dec_start = float(box[5]) - 5

    # roughly get the size of the image
    # size = max(ra_end - ra_start, dec_end - dec_start)

    exoplanets = Exoplanet.objects.filter(
        ra__gt=ra_start, ra__lt=ra_end, dec__gt=dec_start, dec__lt=dec_end)

    list = []
    for planet in exoplanets:

        try:
            vmag = round(float(planet.sy_vmag) * 10) / 10
            designation = planet.hostname + ' - m' + str(vmag)
        except:
            vmag = 0
            designation = planet.hostname

        if vmag <= 15:
            element = {}

            element['ra'] = float(planet.ra)
            element['dec'] = float(planet.dec)

            element['label'] = designation
            element['shape'] = 'exoplanet'
            element['size'] = 20
            element['color'] = 'red'

            list.append(element)

            # if this star as multiple exoplanets, then also draw a green circle
            if planet.sy_pnum > 1:
                element = {}

                element['ra'] = float(planet.ra)
                element['dec'] = float(planet.dec)

                element['label'] = ""
                element['shape'] = 'exoplanet'
                element['size'] = 30
                element['color'] = 'green'

                list.append(element)

    extra = json.dumps(list)
    return extra


def get_asteroids_as_json(observation):
    """
    update the coordinates of all the 1000 asteroid on file
    and draw them on the transient images of my observation
    """
    # update the asteroids table with the data of the observation.
    update_asteroid_table_ephemeris(observation.date)

    # roughly cut out the coordinate box of the image, but take a wide margin

    box = observation.box.split(',')
    ra_end = float(box[0]) + 5
    dec_end = float(box[1]) + 5
    ra_start = float(box[4]) - 5
    dec_start = float(box[5]) - 5

    asteroids = Asteroid.objects.filter(ra__gt=ra_start, ra__lt=ra_end, dec__gt=dec_start, dec__lt=dec_end)

    list = []
    for asteroid in asteroids:

        designation = f'{asteroid.designation} - m{asteroid.visual_magnitude}'

        if asteroid.visual_magnitude <= 15:
            element = {}

            element['ra'] = float(asteroid.ra)
            element['dec'] = float(asteroid.dec)

            element['label'] = designation
            element['shape'] = 'asteroid'
            element['size'] = 20
            element['color'] = 'yellow'

            list.append(element)

    extra = json.dumps(list)
    return extra



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
        asteroid.visual_magnitude = round(details['visual_magnitude'],1)
        asteroid.timestamp = timestamp
        print(f'{designation} - m{asteroid.visual_magnitude}')
        asteroid.save()

