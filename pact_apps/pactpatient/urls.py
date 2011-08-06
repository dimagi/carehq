from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^patient/new$', 'pactpatient.views.new_patient', name='new_pactpatient'),
)
