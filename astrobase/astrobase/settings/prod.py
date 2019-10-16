from astrobase.settings.base import *

# Import production setting must remain False.
DEBUG = False

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

DATA_HOST = "http://uilennest.net/static/astrobase"