import os
from astrobase.settings.base import *

# Import production setting must remain False.
DEBUG = True

ALLOWED_HOSTS = ["*"]

# True: Enables a header that disables the UA from 'clever' automatic mime type sniffing.
# http://django-secure.readthedocs.io/en/latest/settings.html#secure-content-type-nosniff
# https://stackoverflow.com/questions/18337630/what-is-x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = True

# True: Enables a header that tells the UA to switch on the XSS filter.
# http://django-secure.readthedocs.io/en/latest/middleware.html#x-xss-protection-1-mode-block
SECURE_BROWSER_XSS_FILTER = True

# Prevents the site from being deployed within a iframe.
# This prevent click-jacking attacks.
# See; https://docs.djangoproject.com/en/1.11/ref/clickjacking/
X_FRAME_OPTIONS = 'DENY'
#####################################################

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '/shared/astrobase.sqlite3'),
    },
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []

# this works, reverse-proxy through apache
# STATIC_URL = '/static_astrobase/'
STATIC_URL = '/my_astrobase/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'my_static_files')

MEDIA_URL = 'https://localhost/'
MEDIA_ROOT = '/data/astrobase/landing_pad'

ASTROMETRY_HOST = "http://nova.astrometry.net/api"
DATA_HOST = "https://uilennest.net/astrobase/data"

LOGIN_REDIRECT_URL = "https://uilennest.net/astroview/login"
LOGOUT_REDIRECT_URL = "https://uilennest.net/astroview/logout"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

MY_ASTEROIDS = "/shared/asteroids.txt"