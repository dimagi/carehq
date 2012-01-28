from django.conf.urls.defaults import *
from issuetracker import issue_constants
#from haystack.views import SearchView
from permissions.models import Actor



urlpatterns = patterns ('issuetracker.views',
    url(r'^filter/(?P<filter_id>[0-9a-f]{32})$', 'view_filter', name="view-filter"),
    url(r'^issue/(?P<issue_id>[0-9a-f]{32})$', 'manage_issue', name="manage-issue"),
    url(r'^issue/(?P<issue_id>[0-9a-f]{32})/feed$', 'issue_newsfeed', name='issue-newsfeed'),
    url(r'^issues/all$', 'all_issues'),


    #debug views for issue managemen{{issue.get_absolute_urlt
    url(r'^issuetracker/reference', 'debug_reference'), #reference view to see all the different ways to view issues

    url(r'^issuetracker/users/$', 'all_users'), #choose all users in system
    url(r'^issues/roles/$', 'all_roles'), #choose all roles in system
    url(r'^issuetracker/patients/$', 'all_patients'), #choose all patients in system

    url(r'^issuetracker/actors/(?P<actor_id>[0-9a-zA-Z]{32})/', 'actor_issues'), #Cases per user by role
    url(r'^issuetracker/roles/(?P<role_id>[0-9a-f]{32})/', 'role_issues'), #issues for a user-role in system
    url(r'^issuetracker/patients/(?P<patient_id>[0-9a-f]{32})/', 'patient_issues'), #issues for a user-role in system



    
    #url(r'^issue/(?P<issue_id>[0-9a-f]{32})/close$', 'issuetrackerclose_or_resolve_issue', {'edit_mode': constants.ISSUE_STATE_CLOSED}, name="close-issue"),
    #url(r'^issue/(?P<issue_id>[0-9a-f]{32})/resolve$', 'issuetrackerclose_or_resolve_issue', {'edit_mode': constants.ISSUE_STATE_RESOLVED}, name="resolve-issue"),
    #url(r'^issue/(?P<issue_id>[0-9a-f]{32})/edit$', 'issuetrackeredit_issue', name="edit-issue"),
    #url(r'^issue/(?P<issue_id>[0-9a-f]{32})/comment$', 'issuetrackerissue_comment', name="issue-comment"),
   
   #haystack
   #url(r'^search/$', SearchView(), name='haystack_search'),
   
   
)    
    
