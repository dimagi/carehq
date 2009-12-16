from django.conf.urls.defaults import *
from django.contrib.auth import authenticate, login

urlpatterns = patterns('',
    (r'^styleguide$', 'ashandapp.views.styleguide'),
    (r'^grids/$', 'ashandapp.views.datagrids'),
    (r'^dashboard/$', 'ashandapp.views.dashboard'),    
)    
    
