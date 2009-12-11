from django.conf.urls.defaults import *
import settings

urlpatterns =  []

for appname in settings.INSTALLED_APPS:
    try:    
        # import the single "urlpatterns" attribute        
        module = __import__(appname, {}, {}, ['urls'])                
        if hasattr(module,'urls'):            
            urls_module = "%s.urls" % (appname)            
            urlpatterns += patterns('',(r'^%s/' % appname, include(urls_module)))        
    except Exception, e:
        print str(e)



    


#from django.conf.urls.defaults import *

#urlpatterns = patterns('',
#    (r'^weblog/',        include('django_website.apps.blog.urls.blog')),
#    (r'^documentation/', include('django_website.apps.docs.urls.docs')),
#    (r'^comments/',      include('django.contrib.comments.urls')),
#)