import os
from astrobase.settings.base import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]
CORS_ORIGIN_ALLOW_ALL = True

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = ''
MEDIA_URL = ''
#MEDIA_URL = 'http://localhost:8000/my_astrobase/'

DATA_HOST = "https://web-of-wyrd.nl/data_on_yggdrasil/astrobase/data"

LOGIN_REDIRECT_URL = "http://localhost:3000/astroview/login"
LOGOUT_REDIRECT_URL = "http://localhost:3000/astroview/logout"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

MY_ASTEROIDS_ROOT = "asteroids.txt"
MY_HIPPARCOS_ROOT = "hip_main.dat"
MY_EXOPLANETS_ROOT = "exoplanets.csv"
MY_HYG_ROOT = "hygdata.sqlite3"