from django.conf.urls.defaults import *


#(r'^projects/(?P<project_id>\d+)/?$', 'buildmanager.views.show_project'),
urlpatterns = patterns ('',
    (r'^provider/caselist$', 'pact-carehq.views.get_caselist'),
    (r'^submit$', 'pact-carehq.views.post'),
    (r'^receiver/submit/.*$', 'pact-carehq.views.post'),

    (r'^progress_notes/$', 'pact-carehq.views.show_submits_by_me'),
    url(r'^progress_notes/(?P<doc_id>[0-9a-f]{32})$', 'pact-carehq.views.show_progress_note', name='show_progress_note'),
    url(r'^progress_notes/(?P<doc_id>[0-9a-f]{32})/edit$', 'pact-carehq.views.edit_progress_note', name='edit_progress_note'),


)
