import requests

try:
    from skyfield.api import load
    from skyfield.data import mpc
    from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
    import ephem
except:
    # weird bug, importing skyfield doesn't work in debugger
    # works fine in production
    pass

import datetime

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%Y-%m-%d %H:%M:%SZ"
DJANGO_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

# fetch properties of the orbits of a minor planet by name
def get_minor_planets_webservice(name, timestamp):
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

    #yh = ephem.readdb("C/2002 Y1 (Juels-Holvorcem),e,103.7816," +
    #                  "166.2194,128.8232,242.5695,0.0002609,0.99705756,0.0000," +
    #                  "04/13.2508/2003,2000,g  6.5,4.0")
    yh = ephem.readdb(line)

    # convert timestamp to proper observing time for ephem to understand
    # 1984/5/30 16:22:56
    # "%Y-%m-%dT%H:%M:%SZ"
    observing_time = timestamp.strftime('%Y/%m/%d %H:%M:%S')
    yh.compute(observing_time)

    print(yh.name)
    print("%s %s" % (yh.ra, yh.dec))
    print("%s %s" % (ephem.constellation(yh), yh.mag))

    ephemeris = {}
    ephemeris['name'] = yh.name
    ephemeris['timestamp'] = observing_time
    ephemeris['ra'] = str(yh.ra)
    ephemeris['dec'] = str(yh.dec)
    ephemeris['magnitude'] = str(yh.mag)

    result = {}
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
    result['distance'] = str(distance)
    result['magnitude_g'] = row['magnitude_g']
    result['magnitude_k'] = row['magnitude_k']
    result['row'] = row
    return result


