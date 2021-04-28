from astrobase.settings.base import *
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]
CORS_ORIGIN_ALLOW_ALL = True

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []

MEDIA_URL = 'http://localhost/'
MEDIA_ROOT = 'd:/my_astrobase/landing_pad'
DATA_HOST = "http://uilennest.net/astrobase/data"

LOGIN_REDIRECT_URL = "http://localhost:3000/astroview/login"
LOGOUT_REDIRECT_URL = "http://localhost:3000/astroview/logout"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

MY_ASTEROIDS = "asteroids.txt"