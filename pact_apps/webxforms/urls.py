from django.conf.urls.defaults import *

urlpatterns = patterns('webxforms.views',

                       url(r'^pact/interaction/new/(?P<case_id>[\w\-]+)/(?P<interaction>.*)/$', 'new_xform_interaction', name="new_xform_interaction"),
                       url(r'^pact/interaction/edit/(?P<xform_id>[\w\-]+)/$', 'edit_xform_interaction', name="edit_xform_interaction"),

                       #form entry callback
                       url(r'^pact/formentry/callback/(?P<case_id>[\w\-]+)$', 'touchform_callback', name="touchform_callback"),

    #touchforms specific stuff
                       url(r'^a/pact/cloudcare/api/cases$', 'get_cases', name="touchform_callback"),
)



