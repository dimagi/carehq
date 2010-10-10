from django.conf.urls.defaults import *


#(r'^projects/(?P<project_id>\d+)/?$', 'buildmanager.views.show_project'),
urlpatterns = patterns ('',
    (r'^provider/caselist$', 'pactcarehq.views.get_caselist'),
    (r'^submit$', 'pactcarehq.views.post'),
    (r'^receiver/submit/.*$', 'pactcarehq.views.post'),

    (r'^progress_notes/$', 'pactcarehq.views.show_submits_by_me'),
    url(r'^progress_notes/(?P<doc_id>[0-9a-f]{32})$', 'pactcarehq.views.show_progress_note', name='show_progress_note'),
    url(r'^progress_notes/(?P<doc_id>[0-9a-f]{32})/edit$', 'pactcarehq.views.edit_progress_note', name='edit_progress_note'),


)
