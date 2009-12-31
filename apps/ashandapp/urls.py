from django.conf.urls.defaults import *
from django.contrib.auth import authenticate, login

urlpatterns = patterns('',                                              
    (r'^styleguide$', 'ashandapp.views.styleguide'),
   
    (r'^users/all$', 'ashandapp.views.users.all'),
    (r'^users/(?P<user_id>\d+)$', 'ashandapp.views.users.single'),    
                
    (r'^careteam/(?P<careteam_id>\d+)$', 'ashandapp.views.careteam.single'),    
    
    (r'^careteam/(?P<careteam_id>\d+)/new/inquiry$', 'ashandapp.views.cases.inquiry.new_inquiry'),
    (r'^careteam/(?P<careteam_id>\d+)/new/issue$', 'ashandapp.views.cases.issue.new_issue'),
    
    
    #main navigation tabs
    (r'^$', 'ashandapp.views.dashboard.my_dashboard'),
    url(r'^profile/$', 'ashandapp.views.users.single', name="profile"),
    (r'^network/$', 'ashandapp.views.careteam.network.my_network'),

)    
    
