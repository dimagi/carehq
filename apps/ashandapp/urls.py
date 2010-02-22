from django.conf.urls.defaults import *
from django.contrib.auth import authenticate, login

urlpatterns = patterns('',                                              
    (r'^users/(?P<user_id>\d+)$', 'ashandapp.views.users.single'),
    (r'^my_admin/jsi18n', 'django.views.i18n.javascript_catalog'),
    
    
    
    #main navigation tabs
    url(r'^$', 'ashandapp.views.dashboard.my_dashboard', name='my_dashboard'),
    url(r'^tabbed/$', 'ashandapp.views.dashboard.my_dashboard_tab', name='my_dashboard_tab'),
    url(r'^tabbed/json/$', 'ashandapp.views.dashboard.get_json_for_paging', name='json_string'),
    
    #generic json case queryset
    url(r'^grid/cases/(?P<content_type_name>.*)/(?P<content_uuid>[0-9a-f]{32})$', 'ashandapp.views.cases.queries.grid_cases_for_object', name='cases-for-obj-view'),
            
    #specific grid views by user login
    url(r'^grid/cases/provider$', 'ashandapp.views.cases.queries.grid_provider_patient_cases', name='grid_provider_patient_cases'),
    url(r'^grid/cases/triage$', 'ashandapp.views.cases.queries.grid_triage_cases', name='grid_triage_cases'),
    url(r'^grid/cases/caregiver$', 'ashandapp.views.cases.queries.grid_caregiver_cases', name='grid_caregiver_cases'),
    
    url(r'^grid/cases/recent$', 'ashandapp.views.cases.queries.grid_recent_activity', name='grid_recent_activity'),


    
    url(r'^profile/$', 'ashandapp.views.users.my_profile', name="my_profile"),
    url(r'^careteam/mine/$', 'ashandapp.views.careteam.network.my_careteam', name='my_careteam'),
    url(r'^patients/mine/$', 'ashandapp.views.careteam.network.my_patients', name='my_patients'),
    url(r'^recipients/$', 'ashandapp.views.careteam.network.my_care_recipients', name='my_care_recipients'),
    
    url(r'^careteam/(?P<careteam_id>[0-9a-f]{32})/cases$', 'ashandapp.views.careteam.ajax.view_careteam_cases', name='careteam-cases-tabpage'),
    url(r'^grid/careteam/(?P<careteam_id>[0-9a-f]{32})/cases$', 'ashandapp.views.cases.queries.grid_careteam_cases', name='careteam-cases-grid'),
    
    
    #careteam specific links
    url(r'^careteam/(?P<careteam_id>[0-9a-f]{32})$', 'ashandapp.views.careteam.single', name='view-careteam'),
            
    (r'^careteam/(?P<careteam_id>[0-9a-f]{32})/new/question$', 'ashandapp.views.cases.create.new_question'),
    (r'^careteam/(?P<careteam_id>[0-9a-f]{32})/new/issue$', 'ashandapp.views.cases.create.new_issue'),

)    
    
