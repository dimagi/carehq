from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^patient/new$', 'patient.views.new_patient', name='new_patient'),
)