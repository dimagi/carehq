#URLS for your patient management should be managed by the app that subclasses the patient model.

from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from patient.views import PatientListView, PatientSingleView
from shinepatient.models import ShinePatient

urlpatterns = patterns('',
    #url(r'^shine/$', 'patient.views.list_patients', name='shine_home'),
    url(r'^shine/$', PatientListView.as_view(template_name='shinepatient/patient_list.html', patient_type=ShinePatient, create_patient_viewname='shine_create_patient_touch'), name='shine_home'),


    #url(r'^shine/patient/new/django$', 'shinepatient.views.new_patient_django', name='shine_create_patient_django'),
    url(r'^shine/patient/new$', 'shinepatient.views.new_patient_touch', name="shine_create_patient_touch"),
    url(r'^shine/patient/new/callback$', 'shinepatient.views.newpatient_callback', name="newshinepatient_callback"),

#    url(r'^shine/patient/single/(?P<patient_id>[0-9a-fA-Z]{25,32})/$', 'patient.views.single_patient',
#        name='shine_single_patient', kwargs={"template": "shinepatient/single_patient.html"}),


    url(r'^shine/patient/single/(?P<patient_guid>[0-9a-fA-Z]{25,32})/$',
            PatientSingleView.as_view(template_name='shinepatient/single_patient.html'), name='shine_single_patient'),

    url(r'^shine/case/list$', 'shinepatient.views.list_cases', name='shine_case_list'), 
    url(r'^shine/case/(?P<case_id>[0-9a-fA-Z]{25,32})/$', 'shinepatient.views.single_case', 
        name='shine_case_details'),
)

