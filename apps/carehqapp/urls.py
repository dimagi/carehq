from django.conf.urls.defaults import *
from django.contrib.auth import authenticate, login

urlpatterns = patterns('',
        url(r'^$', 'carehqapp.views.home.home_view', name='home'),
        url(r'^dashboard$', 'carehqapp.views.dashboard.dashboard_view', name='dashboard'),
        url(r'^profile$', 'carehqapp.views.account.my_profile', name='my_profile'),
        url(r'^cases$', 'carehqapp.views.cases.case_list', name='case_list'),




#
#    (r'^users/(?P<user_id>\d+)$', 'ashandapp.views.users.single'),
#    (r'^my_admin/jsi18n', 'django.views.i18n.javascript_catalog'),
#
#    #main navigation tabs
#    url(r'^$', 'ashandapp.views.filters.list_cases', name='list_cases'),
#    url(r'^tabbed/json/$', 'ashandapp.views.dashboard.get_json_for_paging', name='json_string'),
#
#    #generic json case queryset
#    url(r'^grid/cases/(?P<content_type_name>.*)/(?P<content_uuid>[0-9a-f]{32})$', 'ashandapp.views.cases.queries.grid_cases_for_object', name='cases-for-obj-view'),
#
#    #specific grid views by user login
#    url(r'^grid/cases/provider$', 'ashandapp.views.cases.queries.grid_provider_patient_cases', name='grid_provider_patient_cases'),
#    url(r'^grid/cases/triage$', 'ashandapp.views.cases.queries.grid_triage_cases', name='grid_triage_cases'),
#    url(r'^grid/cases/caregiver$', 'ashandapp.views.cases.queries.grid_caregiver_cases', name='grid_caregiver_cases'),
#    url(r'^grid/cases/recent$', 'ashandapp.views.cases.queries.grid_recent_activity', name='grid_recent_activity'),
#
#
#
#    url(r'^profile/$', 'ashandapp.views.users.my_profile', name="my_profile"),
#    url(r'^careteam/mine/$', 'ashandapp.views.careteam.network.my_careteam', name='my_careteam'),
#    url(r'^patients/mine/$', 'ashandapp.views.careteam.network.my_patients', name='my_patients'),
#    url(r'^recipients/$', 'ashandapp.views.careteam.network.my_care_recipients', name='my_care_recipients'),
#
#    url(r'^mobile/caselist$', 'ashandapp.views.mobile.case_list', name='mobile_case_list'),
#    url(r'^mobile/newprovider', 'ashandapp.views.mobile.new_provider', name='new_provider'),
#
#    url(r'^careteam/(?P<careteam_id>[0-9a-f]{32})/cases$', 'carehqapp.views.careteam.ajax.view_careteam_cases', name='careteam-cases-tabpage'),
#    url(r'^grid/careteam/(?P<careteam_id>[0-9a-f]{32})/cases$', 'ashandapp.views.cases.queries.grid_careteam_cases', name='careteam-cases-grid'),
#
#
#    #careteam specific links
#    url(r'^careteam/(?P<careteam_id>[0-9a-f]{32})$', 'carehqapp.views.careteam.single', name='view-careteam'),
#    url(r'^careteam/(?P<careteam_id>[0-9a-f]{32})/careplan$', 'carehqapp.views.careteam.single_careplan', name='view-careteam-careplan'),
#    url(r'^careteam/(?P<careteam_id>[0-9a-f]{32})/history$', 'carehqapp.views.careteam.single_history', name='view-careteam-history'),
#
#    (r'^careteam/(?P<careteam_id>[0-9a-f]{32})/new/question$', 'ashandapp.views.cases.create.new_question'),
#    (r'^careteam/(?P<careteam_id>[0-9a-f]{32})/new/issue$', 'ashandapp.views.cases.create.new_issue'),

)    
    
