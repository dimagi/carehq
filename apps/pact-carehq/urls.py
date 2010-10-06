from django.conf.urls.defaults import *


#(r'^projects/(?P<project_id>\d+)/?$', 'buildmanager.views.show_project'),
urlpatterns = patterns ('',
    (r'^caselist$', 'pact-carehq.views.get_caselist'),
)
