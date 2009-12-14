from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^styleguide$', 'ashandapp.views.styleguide'),
    (r'^grids/$', 'ashandapp.views.datagrids'),
    (r'^dashboard/$', 'ashandapp.views.dashboard'),
)    
    
