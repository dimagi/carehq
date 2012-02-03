from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^account/$', 'account.views.landing', name='account_landing'),
    url(r'^account/profile/request$', 'account.views.request_profile', name='request_profile'),
    url(r'^account/setactor/(?P<actor_id>[0-9a-zA-Z]{25,32})/$', 'account.views.set_current_actor',name='set_current_actor') ,
)
