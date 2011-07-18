import logging

# Site-specific configuration settings for ASHand
# Definitions of these settings can be found at
# http://docs.djangoproject.com/en/dev/ref/settings/

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
import os
from django.conf.urls.defaults import patterns, include


XFORMS_PLAYER_URL = "http://localhost:4444/"
AUTH_PROFILE_MODULE = 'actorprofile.ClinicalUserProfile'

# shine
#BASE_TEMPLATE = "shinepatient/shine_base.html"

#####
#Shared Settings
#####

ADMINS = (
    ('foo', 'foo@dimagi.com'),
)

import restkit
restkit.set_logging(level=logging.ERROR)
import couchdbkit
couchdbkit.set_logging(level=logging.ERROR)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

filepath = os.path.abspath(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(filepath,'mediafiles')
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/media/admin/'
AUX_MEDIA_DIRS = { }

# Extra site information.
SITE_ID = 1
SITE_ROOT = '/'
DEBUG = True

# Email setup
# email settings: these ones are the custom hq ones
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD=""
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT=587
EMAIL_USE_TLS=True

# Unique secret key. Don't share this with anybody.
# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

THUMBNAIL_DEBUG = True

DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'couchdebugpanel.CouchDBLoggingPanel',
    )



LOGIN_TEMPLATE='pactregistration/login.html'
LOGGEDOUT_TEMPLATE='pactregistration/logged_out.html'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'carehq',
        'USER': 'carehq',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
    }
}
# Cache backend settings.
CACHE_BACKEND = 'memcached://localhost:11211/'

#PACT
LOCAL_APPS = (
                #dev, debug
                'devserver',
                'debug_toolbar',
                'couchdebugpanel',

                #core pact
                'pactcarehq',
                'keymaster',
                'dotsview',
                'pactpatient',
                'webxforms',
                
                #shine
                'sorl.thumbnail',
                'slidesview',
                'shineforms',
                'shinepatient',
)

COUCH_SERVER_ROOT = 'localhost:5984'
COUCH_USERNAME = ''
COUCH_PASSWORD = ''
COUCH_DATABASE_NAME = 'carehq'

LOCAL_COUCHDB_APPS = ['pactpatient', 'touchforms.formplayer', 'actorprofile',
                      'dotsview', 'pactcarehq', 'slidesview', "shinepatient" ]

#local settings does this to make this a lot easeir
LOCAL_APP_URLS = patterns('',
    (r'', include('pactcarehq.urls')),
    (r'', include('pactpatient.urls')),
    (r'', include('patient.urls')),
    (r'', include('keymaster.urls')),
    (r'', include('dotsview.urls')),
    (r'', include('auditcare.urls')),
    (r'', include('couchdebugpanel.urls')),
    (r'', include('slidesview.urls')),
    (r'', include('shineforms.urls')),
    (r'', include('shinepatient.urls')),
    (r'^couchlog/', include('couchlog.urls')),
    (r'^phone/', include('casexml.apps.phone.urls')),
    (r'^receiver/', include('receiver.urls')),
    (r'^formplayer/', include('touchforms.formplayer.urls')),
    (r'^webxforms/', include('webxforms.urls')),
    (r'^couchforms/', include('couchforms.urls')),

    #these are the static media for fomsplayer since it's not using the django staticfiles app
    (r'^%s/formplayer/(?P<path>.*)$' % 'media', 'django.views.static.serve', {'document_root': os.path.join(filepath, 'submodules','touchforms','touchforms','formplayer','static') }),
    (r'^%s/(?P<path>.*)$' % 'media', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
)


AUDIT_VIEWS = ['pactcarehq.views.post',]
AUDIT_MODEL_SAVE = [
                    'django.contrib.auth.models.User',
                    'patient.models.BasePatient',
                    'dotsview.models.couchmodels.CObservationAddendum',
                    'dotsview.models.couchmodels.CObservation',
                    ]
DEV_APPS=['couchlog','couchforms','couchexport','patient','actors','keymaster','pactcarehq','dotsview','auditcare', ]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'auditcare.middleware.AuditMiddleware',
    'dimagi.utils.threadlocals.ThreadLocals',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

