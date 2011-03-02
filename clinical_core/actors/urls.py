from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^addprovider/?$', 'clinical_core.actors.views.addProvider', name='addProvider'),
    url(r'^actor/(?P<actor_id>[0-9a-f]{32})/$', 'clinical_core.actors.views.view_actor', name="view_actor"),
)
