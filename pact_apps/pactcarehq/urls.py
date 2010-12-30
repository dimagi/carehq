from django.conf.urls.defaults import *


#(r'^projects/(?P<project_id>\d+)/?$', 'buildmanager.views.show_project'),
urlpatterns = patterns ('',
    (r'^$', 'pactcarehq.views.my_patient_activity'),
    #(r'^$', 'pactcarehq.views.user_submit_tallies'),
    (r'^provider/caselist$', 'pactcarehq.views.get_caselist'),
    (r'^submit$', 'pactcarehq.views.post'),
    (r'^submit/$', 'pactcarehq.views.post'),
    (r'^receiver/submit/.*$', 'pactcarehq.views.post'),
    (r'^receiver/submit$', 'pactcarehq.views.post'),

    (r'^submits/mine$', 'pactcarehq.views.my_submits'),
    (r'^submits/chw/all$', 'pactcarehq.views.all_submits_by_user'),
    (r'^submits/patient/all$', 'pactcarehq.views.all_submits_by_patient'),
    (r'^export/$', 'pactcarehq.views.export_excel_file'),

    (r'^schedules/chw/(?P<username>.*)$', 'pactcarehq.views.chw_calendar_submit_report'),
    (r'^schedules/patient/(?P<patient_id>[0-9a-f]{32})$', 'pactcarehq.views.patient_schedule_report'),

    #(r'^patients/mine$', 'pactcarehq.views.my_patients'),
    (r'^patients/all$', 'pactcarehq.views.patient_list'),
    url(r'^patients/(?P<patient_id>[0-9a-f]{32})$', 'pactcarehq.views.patient_view', name='view_patient'),
    #(r'^patients/(?P<patient_id>[0-9a-f]{32})/schedule/set$', 'pactcarehq.views.set_schedule'),

    url(r'^progress_notes/(?P<doc_id>[0-9a-f]{32})$', 'pactcarehq.views.show_progress_note', name='show_progress_note'),
    url(r'^dots_note/(?P<doc_id>[0-9a-f]{32})$', 'pactcarehq.views.show_dots_note', name='show_dots_note'),
    #url(r'^progress_notes/(?P<doc_id>[0-9a-f]{32})/edit$', 'pactcarehq.views.show_progress_note', name='edit_progress_note'),
    #(r'^dots/', include('dotsview.urls')),
)
