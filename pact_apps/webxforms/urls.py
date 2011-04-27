from django.conf.urls.defaults import *
urlpatterns = patterns ('',
    url(r'^landing$', 'webxforms.views.temp_landing'),
    url(r'^progress_note/new/$', 'webxforms.views.new_progress_note'),
)
