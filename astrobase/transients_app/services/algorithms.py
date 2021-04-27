import requests

try:
    from skyfield.api import load
    from skyfield.data import mpc
    from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
except:
    # weird bug, importing skyfield doesn't work in debugger
    # works fine in production
    pass

import datetime

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%Y-%m-%d %H:%M:%SZ"
DJANGO_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

# fetch properties of the orbits of a minor planet by name
def get_minor_planets_webservice(name):
    url = 'https://minorplanetcenter.net/web_service/search_orbits'

    params = {}
    params['name'] = name
    params['json'] = 1

    # params = {'name': 'eros', 'json': 1}

    r = requests.get(url, params, auth=('mpc_ws', 'mpc!!ws'))
    # t = r.text
    j = r.json()

    # https://astroquery.readthedocs.io/en/latest/mpc/mpc.html

    return j


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
    result['magnitude_g'] = row['magnitude_g']
    result['magnitude_k'] = row['magnitude_k']
    result['row'] = row
    return result