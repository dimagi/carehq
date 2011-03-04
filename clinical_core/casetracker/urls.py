from django.conf.urls.defaults import *
from casetracker import constants
#from haystack.views import SearchView


urlpatterns = patterns ('',


    url(r'^filter/(?P<filter_id>[0-9a-f]{32})$', 'casetracker.views.view_filter', name="view-filter"),
    url(r'^case/(?P<case_id>[0-9a-f]{32})$', 'casetracker.views.manage_case', name="manage-case"),    
    url(r'^case/(?P<case_id>[0-9a-f]{32})/feed$', 'casetracker.views.case_newsfeed', name='case-newsfeed'),
    url(r'^cases/all$', 'casetracker.views.all_cases'),


    #debug views for case management
    url(r'^cases/reference', 'casetracker.views.debug_reference'), #reference view to see all the different ways to view cases

    url(r'^cases/users/$', 'casetracker.views.all_users'), #choose all users in system
    url(r'^cases/roles/$', 'casetracker.views.all_roles'), #choose all roles in system
    url(r'^cases/patients/$', 'casetracker.views.all_patients'), #choose all patients in system

    url(r'^cases/users/(?P<user_id>\d+)/', 'casetracker.views.user_cases'), #Cases per user by role
    url(r'^cases/roles/(?P<role_id>[0-9a-f]{32})/', 'casetracker.views.role_cases'), #cases for a user-role in system
    url(r'^cases/patients/(?P<patient_id>[0-9a-f]{32})/', 'casetracker.views.patient_cases'), #cases for a user-role in system



    
    #url(r'^case/(?P<case_id>[0-9a-f]{32})/close$', 'casetracker.views.close_or_resolve_case', {'edit_mode': constants.CASE_STATE_CLOSED}, name="close-case"),        
    #url(r'^case/(?P<case_id>[0-9a-f]{32})/resolve$', 'casetracker.views.close_or_resolve_case', {'edit_mode': constants.CASE_STATE_RESOLVED}, name="resolve-case"),
    #url(r'^case/(?P<case_id>[0-9a-f]{32})/edit$', 'casetracker.views.edit_case', name="edit-case"),
    #url(r'^case/(?P<case_id>[0-9a-f]{32})/comment$', 'casetracker.views.case_comment', name="case-comment"),
   
   #haystack
   #url(r'^search/$', SearchView(), name='haystack_search'),
   
   
)    
    
