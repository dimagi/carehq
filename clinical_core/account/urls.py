from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^account/$', 'account.views.landing', name='account_landing'),
    url(r'^account/profile/request$', 'account.views.request_profile', name='request_profile'),
)
