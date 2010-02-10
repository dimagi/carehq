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
    url(r'^cases/(?P<content_type_name>.*)/(?P<content_uuid>[0-9a-f]{32})$', 'ashandapp.views.cases.queries.view_cases_for_object', name='cases-for-obj-view'),
    url(r'^json/cases/(?P<content_type_name>.*)/(?P<content_uuid>[0-9a-f]{32})$', 'ashandapp.views.cases.queries.get_cases_for_obj_json', name='cases-for-obj-json'),

    
    #specific json for users
    url(r'^json/view/cases/provider$', 'ashandapp.views.cases.queries.view_json_provider_patient_cases', name='view-cases-for-provider-json'),
    url(r'^json/view/cases/triage$', 'ashandapp.views.cases.queries.view_json_triage_cases', name='view-cases-for-triage-json'),
    url(r'^json/view/cases/caregiver$', 'ashandapp.views.cases.queries.view_json_caregiver_cases', name='view-cases-for-caregiver-json'),

    
    #specific json for users
    url(r'^json/cases/provider$', 'ashandapp.views.cases.queries.json_provider_patient_cases', name='cases-for-provider-json'),
    url(r'^json/cases/triage$', 'ashandapp.views.cases.queries.json_triage_cases', name='cases-for-triage-json'),
    url(r'^json/cases/caregiver$', 'ashandapp.views.cases.queries.json_caregiver_cases', name='cases-for-caregiver-json'),

    

    
    url(r'^profile/$', 'ashandapp.views.users.my_profile', name="my_profile"),
    url(r'^careteam/mine/$', 'ashandapp.views.careteam.network.my_careteam', name='my_careteam'),
    url(r'^patients/mine/$', 'ashandapp.views.careteam.network.my_patients', name='my_patients'),
    url(r'^recipients/$', 'ashandapp.views.careteam.network.my_care_recipients', name='my_care_recipients'),
    
    url(r'^careteam/(?P<careteam_id>[0-9a-f]{32})/ajax/cases$', 'ashandapp.views.careteam.ajax.view_careteam_cases', name='show-cases-ajax'),
    
    #careteam specific links
    url(r'^careteam/(?P<careteam_id>[0-9a-f]{32})$', 'ashandapp.views.careteam.single', name='view-careteam'),
            
    (r'^careteam/(?P<careteam_id>[0-9a-f]{32})/new/question$', 'ashandapp.views.cases.create.new_question'),
    (r'^careteam/(?P<careteam_id>[0-9a-f]{32})/new/issue$', 'ashandapp.views.cases.create.new_issue'),

)    
    
