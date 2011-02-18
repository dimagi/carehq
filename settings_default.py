from django.conf.urls.defaults import patterns, include
# Unique secret key. Don't share this with anybody.
# Make this unique, and don't share it with anybody.
SECRET_KEY = ''


#Local DB Settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Extra site information.
SITE_ID = 1
SITE_ROOT = '/'
DEBUG = True

#cache settings
CACHE_BACKEND = 'file:///tmp/django_cache'

#Email settings
EMAIL_HOST=''
EMAIL_HOST_USER=''
EMAIL_HOST_PASSWORD=''
EMAIL_USE_TLS=True
EMAIL_PORT=587 #for gmail

#Logging settings
DJANGO_LOG_FILE = "/var/log/datahq/datahq.django.log"
LOG_SIZE = 1000000
LOG_LEVEL   = "DEBUG"
LOG_FILE    = "/var/log/datahq/datahq.log"
LOG_FORMAT  = "[%(name)s]: %(message)s"
LOG_BACKUPS = 256 # number of logs to keep

#COUCHDB SETTINGS
COUCH_SERVER_ROOT = 'localhost:5984'
COUCH_USERNAME = 'admin'
COUCH_PASSWORD = ''
COUCH_DATABASE_NAME = '' #your couchdb here.
COUCH_DB_APPS = ['patient','couchforms','couchexport',] #other apps

#App Settings
#tuple of apps you want to add to this carehq instance
LOCAL_APPS = ()
LOCAL_APP_URLS = patterns('',
                          (r'', include('patient.urls'))
                        )
