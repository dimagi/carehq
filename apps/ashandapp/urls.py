from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'ashandapp.views.styleguide'),
    (r'^grids/$', 'ashandapp.views.datagrids'),
)    
    
