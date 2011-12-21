# Django settings for blah project.
import os
import logging

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

filepath = os.path.abspath(os.path.dirname(__file__))

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(filepath,'mediafiles') #media for user uploaded media.  in general this won't be used at all.
STATIC_ROOT = os.path.join(filepath,'staticfiles')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'
STATIC_URL = '/static/' #note, we should be doing a separation here of MEDIA and STATIC.  In practice for us it's one and the same.

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

AUX_MEDIA_DIRS = {
                  #'djblets': os.path.join(filepath,'apps','djblets','media'),                                                 
                 }                    


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'johnny.middleware.LocalStoreClearMiddleware',
    'johnny.middleware.QueryCacheMiddleware',
    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    #'auditcare.middleware.AuditMiddleware',
    #'casetracker.middleware.threadlocals.ThreadLocals', #this is to do the reflexive filter queries
    #'clinical_core.clinical_shared.middleware.identity.CareHQIdentityMiddleware',
    #'tracking.middleware.VisitorTrackingMiddleware',
    #'breadcrumbs.middleware.BreadcrumbsMiddleware',
    'dimagi.utils.threadlocals.ThreadLocals',
    #'carehqapp.middleware.identity.CareHQIdentityMiddleware',
    'smartagent.middleware.UserAgentDetectorMiddleware',
)

AUDIT_VIEWS = [
    #'pactcarehq.views.my_patient_activity',
#    'pactcarehq.views.get_caselist',
#    'pactcarehq.views.patient_list',
#    'pactcarehq.views.patient_view',
#    'dotsview.views.index_couch',
#    'pactcarehq.views.chw_calendar_submit_report',
#    'dotsview.views.get_csv',
]


DIGEST_ENFORCE_NONCE_COUNT = False

ROOT_URLCONF = 'carehq.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
                               'django.core.context_processors.auth', 
                               'django.core.context_processors.debug', 
                               'django.core.context_processors.i18n', 
                               'django.core.context_processors.media',                               
                               'django.core.context_processors.request',
                               'django.core.context_processors.static',
                               'context_processors.base_template',
                               #'touchforms.context_processors.static_workaround',
                               )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django.contrib.webdesign',
    'couchdbkit.ext.django',

    # Core clinical apps #####################
    'tenant',
    'clinical_core.actorpermission',
    'permissions',
    'couchforms',
    'couchexport',
    'soil', 
    'couchlog',
    'dimagi.utils',
    'receiver',
    'django.contrib.flatpages',
    'touchforms.formplayer',
    'patient',
    'auditcare',
    'downloader',
    'casexml.apps.case',
    'casexml.apps.phone',
    'account',
    'carehqadmin',
    'carehq_core',
    'carehq_mobile',
    'casetracker',
    'keymaster',
    'webxforms',
    'djangocouch',
    'hutch',
    #end clinical_core

    #########################
    #third party apps
    'django_digest',
    'djcelery',    # pip install django-celery
    'djkombu',     # pip install django-kombu
    'tastypie',

    'uni_form',
    'smartagent',
    #'south',
    #end third party apps

    ###########################
    #Apps for production use
    'johnny',

    ####################
    #Dev helper apps
    #'gunicorn',
    #'devserver',
    'django_cpserver',
)


#DEV_APPS are the apps in which you care about for unit testing.  These are the BARE MINIMUM
#DEV_APPS=['couchlog', 'couchforms','couchexport','patient','auditcare', 'casexml.apps.case', 'casexml.apps.phone', 'touchforms.formsplayer',]

#to be overrided by localsettings if need be.  These are the BARE MINIMUM
COUCHDB_APPS = ['patient', 'couchforms', 'couchexport','couchlog','auditcare','casexml.apps.case', 'casexml.apps.phone']


INTERNAL_IPS = ('127.0.0.1',)
JOHNNY_MIDDLEWARE_KEY_PREFIX='jc_myproj'


#def custom_show_toolbar(request):
#    return True # Always show toolbar, for example purposes only.

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    #'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
    #'EXTRA_SIGNALS': ['myproject.signals.MySignal'],
    #'HIDE_DJANGO_SQL': False,
}

USE_DJANGO_STATIC_SERVER=True
LOGIN_TEMPLATE='registration/login.html'
LOGGEDOUT_TEMPLATE='registration/logged_out.html'
LOGIN_REDIRECT_URL = '/'
BASE_TEMPLATE = 'base.html'

AUDITABLE_MODELS = [
                    'django.contrib.auth.models.User',
                    #'casetracker.models.Case',
                    #'casetracker.models.CaseEvent',
                    'patient.models.Patient',
                    #'patient.models.PatientIdentifier',
                    ]

TEST_RUNNER = 'dimagi.utils.couch.testrunner.DimagiCouchTestSuiteRunner'


#have sessions expire at browser close for security reasons
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

#celery config
CARROT_BACKEND = "django"


# carehq config
CAREHQ_CREATE_PATIENT_VIEW_NAME = "create_patient"

import os

XFORMS_PATH = "data/xforms"
XFORMS_BOOTSTRAP_PATH = "data/bootstrap_xforms"
XFORMS_PLAYER_URL = "http://localhost:4444/"
TOUCHFORMS_AUTOCOMPL_DATA_DIR = os.path.join(filepath, 'static')


#AUTH_PROFILE_MODULE = 'actorpermission.models.ClinicalUserProfile'
AUTHENTICATION_BACKENDS = (
            'django.contrib.auth.backends.ModelBackend',
            'permissions.backend.ObjectPermissionsBackend',
        )

LOCAL_APPS = ()
LOCAL_COUCHDB_APPS = []

# import local settings if we find them
try:
    #try to see if there's an environmental variable set for local_settings
    import sys
    if os.environ.has_key('SETTINGS_LOCAL'):
        localpath = os.path.dirname(os.environ['SETTINGS_LOCAL'])
        sys.path.insert(0, localpath)
    from settings_local import *
except ImportError, e:
    logging.error("Local settings not found, loading defaults: %s" % (e))
    from settings_default import *

#### Add local apps where specified
INSTALLED_APPS = INSTALLED_APPS + LOCAL_APPS
COUCHDB_APPS = COUCHDB_APPS + LOCAL_COUCHDB_APPS

SMART_AGENT_SETTINGS = {
    'AGENT_DATASET_LOCATION': os.path.join(filepath, 'agents_2011_04_14.pkl')
}

####### Couch Forms & Couch DB Kit Settings #######
def get_server_url(server_root, username, password):
    if username and password:
        return "http://%(user)s:%(pass)s@%(server)s" % \
            {"user": username,
             "pass": password,
             "server": server_root }
    else:
        return "http://%(server)s" % {"server": server_root }

COUCH_SERVER = get_server_url(COUCH_SERVER_ROOT, COUCH_USERNAME, COUCH_PASSWORD)
COUCH_DATABASE = "%(server)s/%(database)s" % {"server": COUCH_SERVER, "database": COUCH_DATABASE_NAME }


XFORMS_POST_URL = "http://%s/%s/_design/couchforms/_update/xform/" % (COUCH_SERVER_ROOT, COUCH_DATABASE_NAME)
COUCHDB_DATABASES = [(app_label, COUCH_DATABASE) for app_label in COUCHDB_APPS ]

