from django.conf.urls.defaults import *
from django.contrib import admin

import settings
import os

urlpatterns =  []

for appname in settings.INSTALLED_APPS:
    try:    
        # import the single "urlpatterns" attribute        
        module = __import__(appname, {}, {}, ['urls'])
        
        if appname == 'django.contrib.admin':
            admin.autodiscover()
            urlpatterns += patterns('',
                                    url(r'^admin/(.*)', admin.site.root),)
            continue
        
        if hasattr(module,'urls'):                        
            urls_module = "%s.urls" % (appname)            
            urlpatterns += patterns('',(r'^%s/' % appname, include(urls_module)))            
            #ok, so it has urls, now for debug purposes
            if hasattr(settings,'USE_DJANGO_STATIC_SERVER') and \
            settings.USE_DJANGO_STATIC_SERVER:
            # does urls.py have a sibling "static" dir?
                mod_dir = os.path.dirname(module.__file__)
                static_dir = "%s/static" % mod_dir
                media_dir = '%s/media' % mod_dir        
                
                if os.path.exists(static_dir):                   
                    urlpatterns += patterns("", url("^media/%s/(?P<path>.*)$" % appname,
                        "django.views.static.serve", {"document_root": static_dir }
                    ))
                if os.path.exists(media_dir):                   
                    urlpatterns += patterns("", url("^media/%s/(?P<path>.*)$" % appname,
                        "django.views.static.serve", {"document_root": static_dir }
                    ))
    except Exception, e:
        print str(e)

#additional media locations pointing for the static server
if hasattr(settings,'AUX_MEDIA_DIRS'):
    if hasattr(settings,'USE_DJANGO_STATIC_SERVER') and settings.USE_DJANGO_STATIC_SERVER:
        for dirname, path in settings.AUX_MEDIA_DIRS.items():
            if os.path.exists(path):
                urlpatterns += patterns("", url("^media/%s/(?P<path>.*)$" % dirname,
                            "django.views.static.serve", {"document_root": path }
                        ))


    


#from django.conf.urls.defaults import *

#urlpatterns = patterns('',
#    (r'^weblog/',        include('django_website.apps.blog.urls.blog')),
#    (r'^documentation/', include('django_website.apps.docs.urls.docs')),
#    (r'^comments/',      include('django.contrib.comments.urls')),
#)