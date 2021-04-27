import requests
# from astroquery.mpc import MPC

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
    # https://astroquery.readthedocs.io/en/latest/mpc/mpc.html

    #result = MPC.query_object('asteroid', name=name)
    #eph = MPC.get_ephemeris(name,start='2021-01-01',step='1h')
    #ra = eph['RA']
    #dec = eph['dec']
    #print(str(ra)+','+str(dec))
    result = {}
    result['name'] = name

    return result