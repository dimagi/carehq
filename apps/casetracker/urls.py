from django.conf.urls.defaults import *

#(r'^projects/(?P<project_id>\d+)/?$', 'buildmanager.views.show_project'),
urlpatterns = patterns ('',
    (r'^cases/$', 'casetracker.views.all_cases'),
    (r'^case/(?P<case_id>\d+)$', 'casetracker.views.view_case'),    
    
    (r'^events/all/$', 'casetracker.views.view_case_events'),
    (r'^events/(?P<case_id>\d+)$', 'casetracker.views.view_case_events'),    
    
    (r'^filters/$', 'casetracker.views.all_filters'),
    (r'^filter/(?P<filter_id>\d+)$', 'casetracker.views.view_filter')        
)    
    
