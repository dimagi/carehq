from django.conf.urls.defaults import *
urlpatterns = patterns ('shineforms.views',

    url(r'^shine/new/bw_questions/(?P<patient_guid>[0-9a-fA-Z]{25,32})$', 'clinical_information',
        name="clinical_information"),


    url(r'^shine/new/bw_order/(?P<patient_guid>[0-9a-fA-Z]{25,32})$', 'new_bloodwork_order',
        name="new_bloodwork_order"),


    url(r'^shine/new/bw_entry/(?P<patient_guid>[0-9a-fA-Z]{25,32})$', 'new_bloodwork_entry',
        name="new_bloodwork_entry"),

    url(r'^shine/new/bw_lab/(?P<patient_guid>[0-9a-fA-Z]{25,32})$', 'new_bloodwork_lab',
        name="new_bloodwork_lab"),


    url(r'^shine/new/discharge/(?P<patient_guid>[0-9a-fA-Z]{25,32})$', 'new_bloodwork_discharge',
        name="new_bloodwork_discharge"),

#form entry callback
    url(r'^shine/formentry/callback/(?P<case_id>[0-9a-fA-Z]{25,32})$', 'shine_form_cb',
        name="shine_form_cb"),


    url(r'^shine/restore$', 'ota_restore',
        name="shineforms_restore"),
    
)
