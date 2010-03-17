from django.conf.urls.defaults import *
from casetracker import constants

#(r'^projects/(?P<project_id>\d+)/?$', 'buildmanager.views.show_project'),
urlpatterns = patterns ('',    
   
   
    url(r'^case/(?P<case_id>[0-9a-f]{32})$', 'casetracker.views.manage_case', name="manage-case"),    
    url(r'^case/(?P<case_id>[0-9a-f]{32})/feed$', 'casetracker.views.case_newsfeed', name='case-newsfeed'),
    
    
    #url(r'^case/(?P<case_id>[0-9a-f]{32})/close$', 'casetracker.views.close_or_resolve_case', {'edit_mode': constants.CASE_STATE_CLOSED}, name="close-case"),        
    #url(r'^case/(?P<case_id>[0-9a-f]{32})/resolve$', 'casetracker.views.close_or_resolve_case', {'edit_mode': constants.CASE_STATE_RESOLVED}, name="resolve-case"),
    #url(r'^case/(?P<case_id>[0-9a-f]{32})/edit$', 'casetracker.views.edit_case', name="edit-case"),
    #url(r'^case/(?P<case_id>[0-9a-f]{32})/comment$', 'casetracker.views.case_comment', name="case-comment"),
   
)    
    
