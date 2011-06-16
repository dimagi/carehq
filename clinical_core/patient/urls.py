#URLS for your patient management should be managed by the app that subclasses the patient model.

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^patient/create$', 'patient.views.new_patient', name='create_patient'),
    url(r'^patient/list$', 'patient.views.list_patients', name='patient_list'),
    url(r'^patient/phone/rm$', 'patient.views.remove_phone', name='remove_phone'),
    url(r'^patient/address/rm$', 'patient.views.remove_address', name='remove_address'),
    url(r'^patient/single/(?P<patient_id>[0-9a-fA-Z]{25,32})/$', 'patient.views.single_patient', name='single_patient'),
    
)

