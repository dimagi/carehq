from django.conf.urls.defaults import *

#(r'^projects/(?P<project_id>\d+)/?$', 'buildmanager.views.show_project'),
urlpatterns = patterns ('',
    (r'^grid_examples$', 'casetracker.views.grid_examples'),
    (r'^case/all/$', 'casetracker.views.all_cases'),
    
    url(r'^case/(?P<case_id>[0-9a-f]{32})$', 'casetracker.views.view_case', name="view-case"),
    
    url(r'^case/(?P<case_id>[0-9a-f]{32})/close$', 'casetracker.views.close_or_resolve_case', {'edit_mode': 'close'}, name="close-case"),        
    url(r'^case/(?P<case_id>[0-9a-f]{32})/resolve$', 'casetracker.views.close_or_resolve_case', {'edit_mode': 'resolve'}, name="resolve-case"),
    
    url(r'^case/(?P<case_id>[0-9a-f]{32})/edit$', 'casetracker.views.edit_case', name="edit-case"),
    url(r'^case/(?P<case_id>[0-9a-f]{32})/comment$', 'casetracker.views.case_comment', name="case-comment"),
    
    (r'^events/all/$', 'casetracker.views.all_case_events'),
    (r'^events/(?P<case_id>[0-9a-f]{32})$', 'casetracker.views.view_case_events'),    
    
    (r'^filters/all/$', 'casetracker.views.all_filters'),
    (r'^filters/(?P<filter_id>\d+)$', 'casetracker.views.view_filter'),

    (r'^newsfeed/cases/$', 'casetracker.views.newsfeed_allcases'),
    
)    
    
