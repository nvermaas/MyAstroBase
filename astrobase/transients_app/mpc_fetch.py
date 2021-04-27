# mpc-fetch.py -- fetches properties of all objects that match search params.

# Sample call to retrieve all Near-Earth-Objects with inclination <= 2 degrees
# and eccentricities >= 0.5:
#  python mpc-fetch.py neo 1 inclination_max 2.0 eccentricity_min 0.5 > data.xml

# For the list of possible search parameters, browse to:
# http://minorplanetcenter.net/web_service.html

# To get results in JSON format instead of xml, add 'json 1' to parameters.

# N.B. This script requires the 'requests' python module:
# $ pip install requests
# If you need pip, see: https://pypi.python.org/pypi/pip


import sys, requests

url = 'https://minorplanetcenter.net/web_service/search_orbits'
# For comet orbits use:  url = 'https://minorplanetcenter.net/web_service/search_comet_orbits'

params = {'name':'eros', 'json': 1}

r = requests.get(url, params, auth = ('mpc_ws', 'mpc!!ws'))

print(r.text)