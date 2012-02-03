#URLS for your patient management should be managed by the app that subclasses the patient model.

from django.conf.urls.defaults import *
from patient.models import BasePatient
from patient.views import PatientListView

urlpatterns = patterns('',
    url(r'^patient/create$', 'patient.views.new_patient', name='create_patient'),
    url(r'^$', PatientListView.as_view(template_name='patient/patient_list.html', patient_type=BasePatient, create_patient_viewname='create_patient'), name='basepatient_list'),
    #url(r'^patient/list$', 'patient.views.list_patients', name='basepatient_list'),
    #url(r'^patient/single/(?P<patient_guid>[0-9a-fA-Z]{25,32})/$', 'patient.views.single_patient', name='view_basepatient'),
)

