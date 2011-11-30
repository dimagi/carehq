from django.conf.urls.defaults import *
urlpatterns = patterns ('shineforms.views',

    url(r'^mepi/interaction/new/(?P<case_id>[0-9a-fA-Z]{25,32})/(?P<interaction>.*)/$', 'new_mepi_interaction',
        name="new_mepi_interaction"),

#form entry callback
    url(r'^shine/formentry/callback/(?P<case_id>[0-9a-fA-Z]{25,32})$', 'shine_form_cb',
        name="shine_form_cb"),

    url(r'^shine/restore$', 'ota_restore',
        name="shineforms_restore"),
    
)
