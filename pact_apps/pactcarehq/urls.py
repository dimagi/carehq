from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponse
from pactcarehq.resources import UserSubmissionResource
from pactcarehq.views import PactPatientSingleView
from patient.views import PatientListView
from pactpatient.models import PactPatient

#(r'^projects/(?P<project_id>\d+)/?$', 'buildmanager.views.show_project'),
submission_resource = UserSubmissionResource()
urlpatterns = patterns ('',
    (r'^pact/api/', include(submission_resource.urls)),

    (r'^$', 'pactcarehq.views.patient_views.my_patient_activity'),
    (r'^uptime$', 'pactcarehq.views.uptime'),
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '%spactcarehq/img/favicon.png' % (settings.STATIC_URL)}),

    (r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", mimetype="text/plain")), #from http://fredericiana.com/2010/06/09/three-ways-to-add-a-robots-txt-to-your-django-project/


    (r'^provider/caselist$', 'pactcarehq.views.get_caselist'),
    (r'^cases$', 'pactcarehq.views.debug_casexml_new'),



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

    (r'^submits/chw/all$', 'pactcarehq.views.chw_list'), #to deprecate
    url(r'^chws/all$', 'pactcarehq.views.chw_views.chw_actor_list', name='chw_actor_list'),
    url(r'^chws/(?P<chw_doc_id>[0-9a-zA-Z]{25,32})$', 'pactcarehq.views.chw_profile', name='pact_chw_profile'),

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
    url(r'^patient/(?P<patient_guid>[0-9a-fA-Z]{25,32})/(?P<view_mode>\w*)$', PactPatientSingleView.as_view(), name='view_pactpatient'),

    url(r'^ajax/getpatientform/$', 'pactcarehq.views.ajax_patient_form_get', name='ajax_patient_form_get'),
    url(r'^ajax/postpatientform/(?P<patient_guid>[0-9a-fA-Z]{25,32})/(?P<form_name>.*)/$', 'pactcarehq.views.ajax_post_patient_form', name='ajax_post_patient_form'),

    url(r'^ajax/getactorform/$', 'pactcarehq.views.ajax_get_actor_form', name='ajax_get_actor_form'),
    url(r'^ajax/postactorform/(?P<doc_id>[0-9a-fA-Z]{25,32})/(?P<form_name>.*)/$', 'pactcarehq.views.ajax_post_actor_form', name='ajax_post_actor_form'),


    url(r'^patient/schedule/rm$', 'pactcarehq.views.remove_schedule', name='remove_schedule'),
    url(r'^patient/phone/rm$', 'pactcarehq.views.remove_phone', name='remove_phone'),
    url(r'^patient/address/rm$', 'pactcarehq.views.remove_address', name='remove_address'),
    url(r'^patient/careteam/provider/rm$', 'pactcarehq.views.api.rm_provider_from_patient', name='rm_provider_from_patient'),
    url(r'^patient/careteam/provider/add$', 'pactcarehq.views.api.do_add_provider_to_patient', name='link_provider_to_patient'),
    url(r'^pact/provider/rm$', 'pactcarehq.views.api.rm_provider', name='rm_pact_provider'),


    #(r'^patients/(?P<patient_id>[0-9a-f]{32})/schedule/set$', 'pactcarehq.views.set_schedule'),

    url(r'^submission/(?P<doc_id>[0-9a-fA-Z]{25,32})$', 'pactcarehq.views.show_submission', name='show_submission'),
    url(r'^submission/pact/rm$', 'pactcarehq.views.rm_dot_submission', name='rm_pact_submission'),

    url(r'^patient/(?P<patient_guid>[0-9a-fA-Z]{25,32})/provider/add$', 'pactcarehq.views.pt_new_or_link_provider', name='pt_new_or_link_provider'),
    url(r'^pact/providers$', 'pactcarehq.views.providers.view_add_pact_provider', name="pact_providers"),
    url(r'^pact/provider/(?P<provider_guid>[0-9a-fA-Z]{25,32})/edit$', 'pactcarehq.views.providers.edit_provider', name='pact_edit_provider'),


        url(r'^actors/(?P<actor_doc_id>[0-9a-f]{32})/(?P<view_mode>\w*)$', 'carehqapp.views.actors.view_actor', name='view_actor'),
        url(r'^patient/api/careteam/actor/rm$', 'carehqapp.views.actors.rm_actor_from_patient', name='rm_actor_from_patient'),
        url(r'^patient/api/careteam/actor/add$', 'carehqapp.views.actors.do_add_actor_to_patient', name='link_actor_to_patient'),
        url(r'^actor/api/rm$', 'carehqapp.views.actors.rm_actor', name='rm_ashand_actor'),
        url(r'^patient/api/(?P<patient_guid>[0-9a-fA-Z]{25,32})/actor/add$', 'carehqapp.views.actors.pt_new_or_link_actor', name='pt_new_or_link_actor'),


    #url(r'^progress_notes/(?P<doc_id>[0-9a-fA-Z]{25,32})$', 'pactcarehq.views.show_progress_note', name='show_progress_note'),
    #url(r'^dots_note/(?P<doc_id>[0-9a-fA-Z]{25,32})$', 'pactcarehq.views.show_dots_note', name='show_dots_note'),
    #url(r'^download/(?P<download_id>[0-9a-fA-Z]{25,32})$', 'pactcarehq.views.file_download'),
)
