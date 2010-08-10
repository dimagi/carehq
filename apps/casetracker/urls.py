from django.conf.urls.defaults import *
from casetracker import constants


urlpatterns = patterns ('',   
    url(r'^filter/(?P<filter_id>[0-9a-f]{32})$', 'casetracker.views.view_filter', name="view-filter"),
    url(r'^case/(?P<case_id>[0-9a-f]{32})$', 'casetracker.views.manage_case', name="manage-case"),    
    url(r'^case/(?P<case_id>[0-9a-f]{32})/feed$', 'casetracker.views.case_newsfeed', name='case-newsfeed'),
    
    #url(r'^case/(?P<case_id>[0-9a-f]{32})/close$', 'casetracker.views.close_or_resolve_case', {'edit_mode': constants.CASE_STATE_CLOSED}, name="close-case"),        
    #url(r'^case/(?P<case_id>[0-9a-f]{32})/resolve$', 'casetracker.views.close_or_resolve_case', {'edit_mode': constants.CASE_STATE_RESOLVED}, name="resolve-case"),
    #url(r'^case/(?P<case_id>[0-9a-f]{32})/edit$', 'casetracker.views.edit_case', name="edit-case"),
    #url(r'^case/(?P<case_id>[0-9a-f]{32})/comment$', 'casetracker.views.case_comment', name="case-comment"),
   
   #haystack
   (r'^search/', include('haystack.urls')),
   
)    
    
