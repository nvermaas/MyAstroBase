import requests
import astropy
from astroquery.mpc import MPC

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
def get_minor_planets_astropy(name):
    url = 'https://minorplanetcenter.net/web_service/search_orbits'

    params = {}
    params['name'] = name
    params['json'] = 1

    # params = {'name': 'eros', 'json': 1}

    r = requests.get(url, params, auth=('mpc_ws', 'mpc!!ws'))
    # t = r.text
    j = r.json()

    # add some empherides to the data
    # https://astroquery.readthedocs.io/en/latest/mpc/mpc.html

    return j