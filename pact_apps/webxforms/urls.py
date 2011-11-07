from django.conf.urls.defaults import *

urlpatterns = patterns('webxforms.views',

                       url(r'^pact/interaction/new/(?P<case_id>[0-9a-fA-Z]{25,32})/(?P<interaction>.*)/$', 'new_xform_interaction', name="new_xform_interaction"),
                       url(r'^pact/interaction/edit/(?P<xform_id>[0-9a-fA-Z]{25,32})/$', 'edit_xform_interaction', name="edit_xform_interaction"),

                       #form entry callback
                       url(r'^pact/formentry/callback/(?P<case_id>[0-9a-fA-Z]{25,32})$', 'touchform_callback', name="touchform_callback"),
)



