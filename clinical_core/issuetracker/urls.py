from django.conf.urls.defaults import *
from issuetracker import constants
#from haystack.views import SearchView


urlpatterns = patterns ('',


    url(r'^filter/(?P<filter_id>[0-9a-f]{32})$', '.views.view_filter', name="view-filter"),
    url(r'^issue/(?P<issue_id>[0-9a-f]{32})$', '.views.manage_issue', name="manage-issue"),
    url(r'^issue/(?P<issue_id>[0-9a-f]{32})/feed$', '.views.issue_newsfeed', name='issue-newsfeed'),
    url(r'^issues/all$', '.views.all_issues'),


    #debug views for issue management
    url(r'^issues/reference', '.views.debug_reference'), #reference view to see all the different ways to view issues

    url(r'^issues/users/$', '.views.all_users'), #choose all users in system
    url(r'^issues/roles/$', '.views.all_roles'), #choose all roles in system
    url(r'^issues/patients/$', '.views.all_patients'), #choose all patients in system

    url(r'^issues/users/(?P<user_id>\d+)/', '.views.user_issues'), #Cases per user by role
    url(r'^issues/roles/(?P<role_id>[0-9a-f]{32})/', '.views.role_issues'), #issues for a user-role in system
    url(r'^issues/patients/(?P<patient_id>[0-9a-f]{32})/', '.views.patient_issues'), #issues for a user-role in system



    
    #url(r'^issue/(?P<issue_id>[0-9a-f]{32})/close$', 'issuetracker.views.close_or_resolve_issue', {'edit_mode': constants.CASE_STATE_CLOSED}, name="close-issue"),
    #url(r'^issue/(?P<issue_id>[0-9a-f]{32})/resolve$', 'issuetracker.views.close_or_resolve_issue', {'edit_mode': constants.CASE_STATE_RESOLVED}, name="resolve-issue"),
    #url(r'^issue/(?P<issue_id>[0-9a-f]{32})/edit$', 'issuetracker.views.edit_issue', name="edit-issue"),
    #url(r'^issue/(?P<issue_id>[0-9a-f]{32})/comment$', 'issuetracker.views.issue_comment', name="issue-comment"),
   
   #haystack
   #url(r'^search/$', SearchView(), name='haystack_search'),
   
   
)    
    
