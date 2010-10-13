from django.conf.urls.defaults import *


#(r'^projects/(?P<project_id>\d+)/?$', 'buildmanager.views.show_project'),
urlpatterns = patterns ('',
    (r'^$', 'pactcarehq.views.dashboard'),
    (r'^provider/caselist$', 'pactcarehq.views.get_caselist'),
    (r'^submit$', 'pactcarehq.views.post'),
    (r'^receiver/submit/.*$', 'pactcarehq.views.post'),

    (r'^progress_notes/$', 'pactcarehq.views.my_submits'),
    (r'^progress_notes/all$', 'pactcarehq.views.all_submits'),
    url(r'^progress_notes/(?P<doc_id>[0-9a-f]{32})$', 'pactcarehq.views.show_progress_note', name='show_progress_note'),
    #url(r'^progress_notes/(?P<doc_id>[0-9a-f]{32})/edit$', 'pactcarehq.views.show_progress_note', name='edit_progress_note'),
    (r'^dots/', include('dotsview.urls')),


)
