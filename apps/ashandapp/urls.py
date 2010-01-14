from django.conf.urls.defaults import *
from django.contrib.auth import authenticate, login

urlpatterns = patterns('',                                              
    (r'^styleguide$', 'ashandapp.views.styleguide'),
   
    (r'^users/all$', 'ashandapp.views.users.all'),
    (r'^users/(?P<user_id>\d+)$', 'ashandapp.views.users.single'),
                
    url(r'^careteam/(?P<careteam_id>\d+)$', 'ashandapp.views.careteam.single', name='view-careteam'),    
    
    (r'^careteam/(?P<careteam_id>\d+)/new/inquiry$', 'ashandapp.views.cases.inquiry.new_inquiry'),
    (r'^careteam/(?P<careteam_id>\d+)/new/issue$', 'ashandapp.views.cases.issue.new_issue'),
    
    
    #main navigation tabs
    url(r'^$', 'ashandapp.views.dashboard.my_dashboard', name='my_dashboard'),
    url(r'^profile/$', 'ashandapp.views.users.my_profile', name="my_profile"),
    url(r'^careteam/mine/$', 'ashandapp.views.careteam.network.my_careteam', name='my_careteam'),
    url(r'^patients/mine/$', 'ashandapp.views.careteam.network.my_patients', name='my_patients'),
    url(r'^recipients/$', 'ashandapp.views.careteam.network.my_care_recipients', name='my_care_recipients'),

)    
    
