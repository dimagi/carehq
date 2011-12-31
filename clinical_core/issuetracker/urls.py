from django.conf.urls.defaults import *
from issuetracker import constants
#from haystack.views import SearchView


urlpatterns = patterns ('',


    url(r'^filter/(?P<filter_id>[0-9a-f]{32})$', '.views.view_filter', name="view-filter"),
    url(r'^case/(?P<case_id>[0-9a-f]{32})$', '.views.manage_case', name="manage-case"),
    url(r'^case/(?P<case_id>[0-9a-f]{32})/feed$', '.views.case_newsfeed', name='case-newsfeed'),
    url(r'^cases/all$', '.views.all_cases'),


    #debug views for case management
    url(r'^cases/reference', '.views.debug_reference'), #reference view to see all the different ways to view cases

    url(r'^cases/users/$', '.views.all_users'), #choose all users in system
    url(r'^cases/roles/$', '.views.all_roles'), #choose all roles in system
    url(r'^cases/patients/$', '.views.all_patients'), #choose all patients in system

    url(r'^cases/users/(?P<user_id>\d+)/', '.views.user_cases'), #Cases per user by role
    url(r'^cases/roles/(?P<role_id>[0-9a-f]{32})/', '.views.role_cases'), #cases for a user-role in system
    url(r'^cases/patients/(?P<patient_id>[0-9a-f]{32})/', '.views.patient_cases'), #cases for a user-role in system



    
    #url(r'^case/(?P<case_id>[0-9a-f]{32})/close$', 'issuetracker.views.close_or_resolve_case', {'edit_mode': constants.CASE_STATE_CLOSED}, name="close-case"),
    #url(r'^case/(?P<case_id>[0-9a-f]{32})/resolve$', 'issuetracker.views.close_or_resolve_case', {'edit_mode': constants.CASE_STATE_RESOLVED}, name="resolve-case"),
    #url(r'^case/(?P<case_id>[0-9a-f]{32})/edit$', 'issuetracker.views.edit_case', name="edit-case"),
    #url(r'^case/(?P<case_id>[0-9a-f]{32})/comment$', 'issuetracker.views.case_comment', name="case-comment"),
   
   #haystack
   #url(r'^search/$', SearchView(), name='haystack_search'),
   
   
)    
    
