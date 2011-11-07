from django.conf.urls.defaults import *
from django.conf import settings
from pactcarehq.views import PactPatientSingleView
from patient.views import PatientListView
from pactpatient.models import PactPatient

#(r'^projects/(?P<project_id>\d+)/?$', 'buildmanager.views.show_project'),
urlpatterns = patterns ('',
    (r'^$', 'pactcarehq.views.my_patient_activity'),
    (r'^uptime$', 'pactcarehq.views.uptime'),
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '%spactcarehq/img/favicon.png' % (settings.STATIC_URL)}),


#    (r'^grouped$', 'pactcarehq.views.my_patient_activity_grouped'),
#    (r'^reduce$', 'pactcarehq.views.my_patient_activity_reduce'),

    (r'^provider/caselist$', 'pactcarehq.views.get_caselist'),
    (r'^cases$', 'pactcarehq.views.debug_casexml_new'),


    url(r'^pact/providers$', 'pactcarehq.views.providers.view_add_pact_provider', name="pact_providers"),

    #where the xforms get submitted to
#    (r'^submit$', 'pactcarehq.views.post'),
#    (r'^submit/$', 'pactcarehq.views.post'),
#    (r'^receiver/submit/.*$', 'pactcarehq.views.post'),
#    (r'^receiver/submit$', 'pactcarehq.views.post'),

    (r'^submit$', 'receiver.views.post'),
    (r'^submit/$', 'receiver.views.post'),
    (r'^receiver/submit/.*$', 'receiver.views.post'),
    (r'^receiver/submit$', 'receiver.views.post'),


    (r'^submits/mine$', 'pactcarehq.views.my_submits'),
    (r'^submits/mine/restore$', 'pactcarehq.views.xml_download'),

    (r'^submits/chw/all$', 'pactcarehq.views.chw_list'),
    (r'^submits/chw/(?P<chw_username>.*)/submits$', 'pactcarehq.views.chw_submits'),


    (r'^submits/submits/bychw$', 'pactcarehq.views.all_submits_by_user'), #to be deprecated
    (r'^submits/patient/all$', 'pactcarehq.views.all_submits_by_patient'),

    (r'^exporter/$', 'pactcarehq.views.export_landing'),
    (r'^export/$', 'pactcarehq.views.export_excel_file'),

    (r'^schedules/chw/(?P<username>.*)$', 'pactcarehq.views.chw_calendar_submit_report'),
    (r'^reports/chw/schedule/all/$', 'pactcarehq.views.chw_calendar_submit_report_all'),
    (r'^schedules/patient/(?P<patient_id>[0-9a-fA-Z]{25,32})$', 'pactcarehq.views.patient_schedule_report'),

    #(r'^patients/all$', 'pactcarehq.views/patient_list'),
    url(r'^patients/all$', PatientListView.as_view(template_name='pactcarehq/patient_list.html', patient_type=PactPatient, create_patient_viewname='pactpatient.views.new_patient'), name='pactpatient_list'),

    #url(r'^patients/(?P<patient_id>[0-9a-fA-Z]{25,32})$', 'pactcarehq.views.patient_view', name='view_pactpatient'),
    url(r'^patient/(?P<patient_guid>[0-9a-fA-Z]{25,32})/$', PactPatientSingleView.as_view(template_name='pactcarehq/pact_patient.html'), name='view_pactpatient'),
    url(r'^ajax/getform/$', 'pactcarehq.views.ajax_get_form', name='ajax_get_form'),
    url(r'^ajax/postform/(?P<patient_guid>[0-9a-fA-Z]{25,32})/(?P<form_name>.*)/$', 'pactcarehq.views.ajax_post_form', name='ajax_post_form'),


    url(r'^patient/schedule/rm$', 'pactcarehq.views.remove_schedule', name='remove_schedule'),
    url(r'^patient/phone/rm$', 'pactcarehq.views.remove_phone', name='remove_phone'),
    url(r'^patient/address/rm$', 'pactcarehq.views.remove_address', name='remove_address'),
    url(r'^patient/careteam/provider/rm$', 'pactcarehq.views.api.rm_provider_from_patient', name='rm_provider_from_patient'),
    url(r'^patient/careteam/provider/add$', 'pactcarehq.views.api.do_add_provider_to_patient', name='link_provider_to_patient'),
    url(r'^pact/provider/rm$', 'pactcarehq.views.api.rm_provider', name='rm_pact_provider'),

    url(r'^pact/provider/(?P<provider_guid>[0-9a-fA-Z]{25,32})/edit$', 'pactcarehq.views.providers.edit_provider', name='pact_edit_provider'),

    #(r'^patients/(?P<patient_id>[0-9a-f]{32})/schedule/set$', 'pactcarehq.views.set_schedule'),

    url(r'^submission/(?P<doc_id>[0-9a-fA-Z]{25,32})$', 'pactcarehq.views.show_submission', name='show_submission'),
    url(r'^patient/(?P<patient_guid>[0-9a-fA-Z]{25,32})/provider/add$', 'pactcarehq.views.pt_new_or_link_provider', name='pt_new_or_link_provider'),

    #url(r'^progress_notes/(?P<doc_id>[0-9a-fA-Z]{25,32})$', 'pactcarehq.views.show_progress_note', name='show_progress_note'),
    #url(r'^dots_note/(?P<doc_id>[0-9a-fA-Z]{25,32})$', 'pactcarehq.views.show_dots_note', name='show_dots_note'),
    #url(r'^download/(?P<download_id>[0-9a-fA-Z]{25,32})$', 'pactcarehq.views.file_download'),
)
