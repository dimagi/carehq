from django.conf.urls.defaults import *
from django.contrib import admin

import settings
import os
import logging
from dimagi.utils.modules import try_import

urlpatterns =  []
admin.autodiscover()

urlpatterns += patterns('',
    (r'^accounts/login/$', 'django.contrib.auth.views.login',
         {"template_name": settings.LOGIN_TEMPLATE}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login',
        ),


    (r'^admin/', include(admin.site.urls)),
    (r'^couchforms/', include('couchforms.urls')),
    (r'^couchlog/', include('couchlog.urls')),
    (r'^djangocouch', include('djangocouch.urls')),
    (r'^formplayer/', include('touchforms.formplayer.urls')),
    (r'', include('account.urls')),
    (r'', include('auditcare.urls')),
    #(r'', include('casetracker.urls')), #TODO
    (r'', include('clinical_core.carehqadmin.urls')),
    (r'', include('downloader.urls')),
    (r'', include('keymaster.urls')),
    (r'^phone/', include('casexml.apps.phone.urls')),
    (r'^mobile/', include('carehq_mobile.urls')),
    (r'^receiver/', include('receiver.urls')),
    (r'^webxforms/', include('webxforms.urls')),


                        # This is a bit kloogey - but since most of these urls don't span
                        # a single namespace (e.g. domain/ and accounts/ for domain app)
                        # we just include the urls at the root.
                        # The correct solution is likely to break apart urls or harmonize
                        # apps so they all have proper prefixing.
                        #(r'', include('actors.urls')), #patient's always here.  carehq cares for patients!
)
if hasattr(settings, 'LOCAL_APP_URLS'):
    #specify for your particular installationwhich local application urls you want to map
    urlpatterns += settings.LOCAL_APP_URLS


# magic static media server (idea + implementation lifted from rapidsms)
for module_name in settings.INSTALLED_APPS:

    # leave django contrib apps alone. (many of them include urlpatterns
    # which shouldn't be auto-mapped.) this is a hack, but i like the
    # automatic per-app mapping enough to keep it. (for now.)
    if module_name.startswith("django."):
        continue

    # attempt to import this app's urls
    module = try_import("%s.urls" % (module_name))
    if not hasattr(module, "urlpatterns"): continue

    # if the MEDIA_URL does not contain a hostname (ie, it's just an
    # http path), and we are running in DEBUG mode, we will also serve
    # the media for this app via this development server. in production,
    # these files should be served directly

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()

#if settings.DEBUG:
#    urlpatterns += patterns('staticfiles.views', url(r'^static/(?P<path>.*)$', 'serve'), )

