#URLS for your patient management should be managed by the app that subclasses the patient model.

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^shine/patient/new$', 'shinepatient.views.new_patient', name='shine_create_patient'),
    url(r'^shine/patient/list$', 'patient.views.list_patients', name='shine_patient_list'), 
    url(r'^shine/patient/single/(?P<patient_id>[0-9a-fA-Z]{25,32})/$', 'patient.views.single_patient', 
        name='shine_single_patient', kwargs={"template": "shinepatient/single_patient.html"}),
    url(r'^shine/case/(?P<case_id>[0-9a-fA-Z]{25,32})/$', 'shinepatient.views.single_case', 
        name='shine_case_details'),
    
    
)

