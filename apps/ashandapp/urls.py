from django.conf.urls.defaults import *
import ashand.views as views

urlpatterns = patterns('',
    (r'^$', 'ashand.views.styleguide'),
    (r'^grids/$', 'ashand.views.datagrids'),
)    
    
