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
MEDIA_ROOT = os.path.join(filepath,'staticmedia')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

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
    #'johnny.middleware.LocalStoreClearMiddleware',
    #'johnny.middleware.QueryCacheMiddleware',
    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
#    'django_digest.middleware.HttpDigestMiddleware',    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',    
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'casetracker.middleware.threadlocals.ThreadLocals', #this is to do the reflexive filter queries
    'ashandapp.middleware.identity.AshandIdentityMiddleware',
    #'tracking.middleware.VisitorTrackingMiddleware',
)

DIGEST_ENFORCE_NONCE_COUNT = False

ROOT_URLCONF = 'ashand.urls'

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
                               )

INSTALLED_APPS = (    
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'couchdbkit.ext.django',
    
    #section ashand apps
    #'casetracker',
    'provider',
    #'patient',
    'ashandapp',
    'careplan',
    #end ashand apps
    
    #clinical_core
    'casetracker',
    'patient',
    'actors',    
    #end clinical_core
    
    
    #third party apps
    'autofixture',
    'reversion',    
    #'django_digest',
    #'tinymce',
    #'debug_toolbar',
    'django_extensions',    
    #'johnny', 
    #'tracking', 
    #'tracking_ext',
    #end third party apps
    
            
    'django.contrib.admin',
    
    'haystack',
    #'gunicorn',
    'devserver',
)

#haystack
HAYSTACK_SITECONF = 'ashand.search_sites'
HAYSTACK_SEARCH_ENGINE = 'solr'
HAYSTACK_SOLR_URL = 'http://127.0.0.1:8983/solr'

INTERNAL_IPS = ('127.0.0.1',)
JOHNNY_MIDDLEWARE_KEY_PREFIX='jc_myproj'

DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
    )

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

CASE_CATEGORIES = (
                   'ashandapp.caseregistry.issue',
                   'ashandapp.caseregistry.system',
                   'ashandapp.caseregistry.question',
                   )

AUDITABLE_MODELS = [
                    'django.contrib.auth.models.User',
                    'casetracker.models.Case',
                    'casetracker.models.CaseEvent',
                    'ashandapp.models.CareTeam',
                    'provider.models.Provider',
                    'patient.models.Patient',
                    'patient.models.PatientIdentifier',                    
                    ]
                    
PATIENT_DOCUMENT_MODEL = 'clinical_core.models.couch.CCareHQPatient'                   

try:
    from settings_local import *
except:
    logging.error("Local settings not found, loading defaults")
    from settings_default import *
    
