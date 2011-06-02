from django.conf.urls.defaults import *
urlpatterns = patterns ('',
    url(r'^landing$', 'webxforms.views.temp_landing'),
    url(r'^progress_note/new/(?P<patient_id>[0-9a-fA-Z]{25,32})$', 'webxforms.views.new_progress_note'),
    url(r'^bw/new/(?P<patient_id>[0-9a-fA-Z]{25,32})$', 'webxforms.views.new_bloodwork'),
)
