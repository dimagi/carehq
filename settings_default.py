# Site-specific configuration settings for Review Board
# Definitions of these settings can be found at
# http://docs.djangoproject.com/en/dev/ref/settings/

# Database configuration
from django.conf.urls.defaults import patterns, include

DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'ashand'
DATABASE_USER = 'root'
DATABASE_PASSWORD = 'password'
DATABASE_HOST = ''
DATABASE_PORT = ''

# Unique secret key. Don't share this with anybody.
# Make this unique, and don't share it with anybody.
SECRET_KEY = ''


# Cache backend settings.
CACHE_BACKEND = 'file:///tmp/django_cache'

# Extra site information.
SITE_ID = 1
SITE_ROOT = '/'
DEBUG = True

EMAIL_HOST=''
EMAIL_HOST_USER=''
EMAIL_HOST_PASSWORD=''
EMAIL_USE_TLS=True
EMAIL_PORT=587

#import logging
#logging.basicConfig (
#       level=logging.DEBUG,
#       format='%(asctime)s %(levelname)s % (message)s',
#       filename='/tmp/review.log',
#       filemode='w+'
#)

#tuple of apps you want to add to this carehq instance
LOCAL_APPS = ()

COUCH_SERVER_ROOT = 'hostname:5984'
COUCH_USERNAME = ''
COUCH_PASSWORD = ''
COUCH_DATABASE_NAME = ''

#array of appnames you need for your couch setup
COUCH_DB_APPS = [
    'patient',
    'couchforms',
    'couchexport',]

LOCAL_APP_URLS = patterns('',
                (r'', include('patient.urls')),
)