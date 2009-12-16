from django.conf.urls.defaults import *
from django.contrib import admin

import settings
import os
import logging

urlpatterns =  []

urlpatterns += patterns('',
                        (r'^accounts/login/$', 'django.contrib.auth.views.login', 
                                                {"template_name": settings.LOGIN_TEMPLATE }),
                        (r'^accounts/logout/$', 'django.contrib.auth.views.logout', 
                                                {"template_name": settings.LOGGEDOUT_TEMPLATE }),
                        #todo, other auth related urls (password_X, reset)
                        )

def setmedia(appname, upats):
    if hasattr(settings,'USE_DJANGO_STATIC_SERVER') and \
    settings.USE_DJANGO_STATIC_SERVER:
    # does urls.py have a sibling "static" dir?
        mod_dir = os.path.dirname(module.__file__)
        static_dir = "%s/static" % mod_dir
        media_dir = '%s/media' % mod_dir        
        
        if os.path.exists(static_dir):                   
            upats += patterns("", url("^media/%s/(?P<path>.*)$" % appname,
                "django.views.static.serve", {"document_root": static_dir }
            ))
        if os.path.exists(media_dir):                   
            upats += patterns("", url("^media/%s/(?P<path>.*)$" % appname,
                "django.views.static.serve", {"document_root": media_dir }
            ))
    return upats


for appname in settings.INSTALLED_APPS:
    try:    
        # import the single "urlpatterns" attribute        
        module = __import__(appname, {}, {}, ['urls'])
        
        if appname == 'django.contrib.admin':
            admin.autodiscover()
            urlpatterns += patterns('',
                                    url(r'^admin/(.*)', admin.site.root),)
            urlpatterns = setmedia('admin', urlpatterns)
            continue
        elif appname == 'django.contrib.auth':
            #All auth stuff will be done by hand.
            continue
        elif appname == 'debug_toolbar':
            #another nasty hack due to the recursion explosion with the url resolver
            continue
        
        if hasattr(module,'urls'):                        
            
            #subdir all the apps?
            #urls_module = "%s.urls" % (appname)            
            #urlpatterns += patterns('',(r'^%s/' % appname, include(urls_module)))                        
            
            #or just put them all to root
            urls_module = "%s.urls" % (appname)            
            module = __import__(urls_module, {}, {}, ["urlpatterns"])
            urlpatterns += module.urlpatterns       
            urlpatterns = setmedia(appname, urlpatterns)
            #ok, so it has urls, now for debug purposes
            
    except Exception, e:
        logging.error("Url load: %s" % str(e))



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