#URLS for your patient management should be managed by the app that subclasses the patient model.

from django.conf.urls.defaults import *
from patient.views import PatientListView
from shinepatient.models import ShinePatient
from shinepatient.views import MepiPatientSingleView

urlpatterns = patterns('',
    url(r'^mepi/patients$', PatientListView.as_view(template_name='shinepatient/patient_list.html', patient_type=ShinePatient, create_patient_viewname='shine_create_patient_touch'), name='shine_home_root'),
    url(r'^mepi/patient/new$', 'shinepatient.views.new_patient_touch', name="shine_create_patient_touch"),
    url(r'^mepi/patient/new/callback$', 'shinepatient.views.newpatient_callback', name="newshinepatient_callback"),
    url(r'^mepi/patient/single/(?P<patient_guid>[0-9a-fA-Z]{25,32})/$', MepiPatientSingleView.as_view(template_name='shinepatient/shine_patient.html'), name='shine_single_patient'),

    url(r'^mepi/patient/single/(?P<patient_guid>[0-9a-fA-Z]{25,32})/upload$', 'shinepatient.views.upload_patient_photo', name='mepi_upload_patient_photo'),
)

