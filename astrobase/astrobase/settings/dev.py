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
DATA_HOST = "http://localhost/data"