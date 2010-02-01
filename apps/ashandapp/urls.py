from django.conf.urls.defaults import *
from django.contrib.auth import authenticate, login

urlpatterns = patterns('',                                              
    (r'^styleguide$', 'ashandapp.views.styleguide'),
   
    (r'^users/all$', 'ashandapp.views.users.all'),
    (r'^users/(?P<user_id>\d+)$', 'ashandapp.views.users.single'),
    
    #main navigation tabs
    url(r'^$', 'ashandapp.views.dashboard.my_dashboard', name='my_dashboard'),
    url(r'^tabbed/$', 'ashandapp.views.dashboard.my_dashboard_tab', name='my_dashboard_tab'),
    url(r'^tabbed/json/$', 'ashandapp.views.dashboard.get_json_for_paging', name='json_string'),
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
    
