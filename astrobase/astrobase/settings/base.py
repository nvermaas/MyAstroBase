"""
Django settings for astrobase project.

Generated by 'django-admin startproject' using Django 2.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'cie-((m#n$br$6l53yash45*2^mwuux*2u)bad5(0flx@krnj9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True
#CSRF_TRUSTED_ORIGINS = ["https://uilennest.net","https://web-of-wyrd.nl"]

# Application definition

INSTALLED_APPS = [
    'backend_app',
    'moon_app',
    'exoplanets',
    'starcharts_app',
    'transients_app',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'django_extensions',
    'rest_framework.authtoken',
    'corsheaders',
    'crispy_forms',
]

MIDDLEWARE = [
    #'django.middleware.cache.UpdateCacheMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'moon_app.middleware.MyMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
]

ROOT_URLCONF = 'astrobase.urls'
CRISPY_TEMPLATE_PACK = 'bootstrap4'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'astrobase.wsgi.application'

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
# Database
DATABASE_ROUTERS = [
    'backend_app.database_router.DefaultRouter',
    'starcharts_app.database_router.StarChartsRouter',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'astrobase.sqlite3'),
    },
    'stars': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'stars.sqlite3'),
    },
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Logging
# https://docs.djangoproject.com/en/1.11/topics/logging/#configuring-logging
# The default configuration: https://github.com/django/django/blob/stable/1.11.x/django/utils/log.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'my_formatter': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(asctime)s] %(message)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'my_formatter',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'my_handler': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'my_formatter',
        },
        'my_file_handler': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'my_formatter',
            'filename': 'logs/astrobase.log'
        },
    },
    'loggers': {
        'backend_app': {
            'handlers': ['my_handler','my_file_handler','mail_admins'],
            'level': 'INFO',
        },
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/


STATIC_URL = '/my_astrobase/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'my_static_files')

try:
    BACKEND_HOST = os.environ['BACKEND_HOST']
except:
    BACKEND_HOST = 'https://uilennest.net/'

# because the backend runs in docker, it can only access a the /shared volume
# at OS level the URL and ROOT are connected through a symbolic link
#MEDIA_URL = 'https://uilennest.net/astrobase/media/'
MEDIA_URL = os.path.join(BACKEND_HOST, 'astrobase/media/')
MEDIA_ROOT = '/landing_pad'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

ASTROMETRY_HOST = "http://nova.astrometry.net/api"
#DATA_HOST = "https://uilennest.net/data_on_yggdrasil/astrobase/data"
DATA_HOST = "https://uilennest.net/astrobase/data"
#DATA_HOST = os.path.join(BACKEND_HOST, 'data_on_yggdrasil/astrobase/data')

ASTROMETRY_HOST = "http://nova.astrometry.net/api"

#REPOSITORY_URL = 'https://uilennest.net/astrobase/repository/'
REPOSITORY_URL = os.path.join(BACKEND_HOST, 'astrobase/repository/')
REPOSITORY_ROOT = '/shared/repository'

#MY_ASTEROIDS_URL = "https://uilennest.net/astrobase/repository/asteroids.txt"
MY_ASTEROIDS_URL = os.path.join(BACKEND_HOST, 'astrobase/repository/asteroids.txt')
MY_ASTEROIDS_ROOT = "/shared/repository/asteroids.txt"

#MY_HIPPARCOS_URL = "https://uilennest.net/astrobase/repository/hip_main.dat"
MY_HIPPARCOS_URL = os.path.join(BACKEND_HOST, 'astrobase/repository/hip_main.dat')
MY_HIPPARCOS_ROOT = "/shared/repository/hip_main.dat"

#MY_EXOPLANETS_URL = "https://uilennest.net/astrobase/repository/exoplanets.csv"
MY_EXOPLANETS_URL = os.path.join(BACKEND_HOST, 'astrobase/repository/exoplanets.csv')
MY_EXOPLANETS_ROOT = "/shared/repository/exoplanets.csv"

#MY_HYG_URL = "https://uilennest.net/astrobase/repository/hygdata.sqlite3"
MY_HYG_URL = os.path.join(BACKEND_HOST, 'astrobase/repository/hygdata.sqlite3')
MY_HYG_ROOT = "/shared/repository/hygdata.sqlite3"

MY_STARLABELS_ROOT = "/shared/repository/starlabels.sqlite3"