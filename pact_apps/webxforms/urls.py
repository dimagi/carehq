from django.conf.urls.defaults import *
urlpatterns = patterns ('',
    url(r'^progress_note/new/(?P<patient_id>[0-9a-fA-Z]{25,32})$', 'webxforms.views.new_progress_note'),
    url(r'^bw/new/(?P<patient_id>[0-9a-fA-Z]{25,32})$', 'webxforms.views.new_bloodwork'),
    url(r'^dots/new/(?P<patient_id>[0-9a-fA-Z]{25,32})$', 'webxforms.views.new_dots'),

    url(r'^progress_note/edit/(?P<doc_id>[0-9a-fA-Z]{25,32})$', 'webxforms.views.edit_progress_note'),
    url(r'^bw/edit/(?P<doc_id>[0-9a-fA-Z]{25,32})$', 'webxforms.views.edit_bloodwork'),



    url(r'^mepi/interaction/new/(?P<case_id>[0-9a-fA-Z]{25,32})/(?P<interaction>.*)/$', 'new_mepi_interaction',
        name="new_mepi_interaction"),

    #form entry callback
    url(r'^shine/formentry/callback/(?P<case_id>[0-9a-fA-Z]{25,32})$', 'shine_form_cb',
        name="shine_form_cb"),

    url(r'^shine/restore$', 'ota_restore',
        name="shineforms_restore"),
)
