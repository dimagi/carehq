from django.conf.urls.defaults import *
from django.contrib.auth import authenticate, login

urlpatterns = patterns('',
    (r'^styleguide$', 'ashandapp.views.styleguide'),
    (r'^grids/$', 'ashandapp.views.datagrids'),
    
    (r'^users/all$', 'ashandapp.views.all_users'),
    (r'^users/(?P<user_id>\d+)$', 'ashandapp.views.view_user'),        
    (r'^careteam/(?P<careteam_id>\d+)$', 'ashandapp.views.view_careteam'),
    (r'^$', 'ashandapp.views.dashboard'),
)    
    
