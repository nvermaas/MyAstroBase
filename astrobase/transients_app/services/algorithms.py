import requests
# from astroquery.mpc import MPC
import skyfield
from skyfield.api import load
from skyfield.data import mpc
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
    # https://rhodesmill.org/skyfield/example-plots.html#drawing-a-finder-chart-for-comet-neowise
    # https://astroquery.readthedocs.io/en/latest/mpc/mpc.html
    ts = load.timescale()
    t = ts.utc(2020, 5, 13, 10, 32)
    eph = load('de421.bsp')
    astrometric = eph['earth'].at(t).observe(eph['psyche'])
    ra, dec, distance = astrometric.radec()
    print(ra, dec, sep='\n')

    with load.open(mpc.COMET_URL) as f:
        comets = mpc.load_comets_dataframe(f)

    comets = (comets.sort_values('reference')
              .groupby('designation', as_index=False).last()
              .set_index('designation', drop=False))


    #result = MPC.query_object('asteroid', name=name)
    #eph = MPC.get_ephemeris(name,start='2021-01-01',step='1h')
    #ra = eph['RA']
    #dec = eph['dec']
    #print(str(ra)+','+str(dec))
    result = {}
    result['name'] = name

    return result