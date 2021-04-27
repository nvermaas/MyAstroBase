import requests

# fetch properties of the orbits of a minor planet by name
def get_minor_planets(name):
    url = 'https://minorplanetcenter.net/web_service/search_orbits'

    params = {}
    params['name'] = name
    params['json'] = 1

    # params = {'name': 'eros', 'json': 1}

    r = requests.get(url, params, auth=('mpc_ws', 'mpc!!ws'))
    # t = r.text
    j = r.json()

    return j