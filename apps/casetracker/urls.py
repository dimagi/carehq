from django.conf.urls.defaults import *

#(r'^projects/(?P<project_id>\d+)/?$', 'buildmanager.views.show_project'),
urlpatterns = patterns ('',
    (r'^grid_examples$', 'casetracker.views.grid_examples'),
    (r'^case/all/$', 'casetracker.views.all_cases'),
    url(r'^case/(?P<case_id>\d+)$', 'casetracker.views.view_case', name="view-case"),    
    
    (r'^events/all/$', 'casetracker.views.all_case_events'),
    (r'^events/(?P<case_id>\d+)$', 'casetracker.views.view_case_events'),    
    
    (r'^filters/all/$', 'casetracker.views.all_filters'),
    (r'^filters/(?P<filter_id>\d+)$', 'casetracker.views.view_filter')        
)    
    
