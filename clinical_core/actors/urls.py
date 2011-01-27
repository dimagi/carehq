from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^addprovider/?$', 'clinical_core.actors.views.addProvider', name='addProvider'),
)
