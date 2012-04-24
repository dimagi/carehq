from django.conf.urls.defaults import url, patterns
#from shinecarehq.views import MepiPatientListView

urlpatterns = patterns('shinecarehq.views',
    #url(r'^$', 'patient_dashboard', name='mepi_dashboard'),
    #url(r'^$', MepiPatientListView.as_view(template_name='shinecarehq/patient_dashboard.html', patient_type=ShinePatient, create_patient_viewname='shine_create_patient_touch', couch_view='shinepatient/shine_patients'), name='mepi_dashboard'),
    (r'^uptime$', 'uptime'),
    url(r'^$', 'case_dashboard', name='mepi_dashboard'),
#    url(r'^mepi/cases/all$', 'all_cases',  name='mepi_all_cases'),
#    url(r'^mepi/cases/mine$', 'my_cases',  name='mepi_my_cases'),

    url(r'^mepi/dashboard/progress$', 'clinical_dashboard', name='clinical_dashboard'),
    url(r'^mepi/dashboard/hiv$', 'hiv_dashboard', name='hiv_dashboard'),
    url(r'^mepi/dashboard/labs$', 'labs_dashboard', name='labs_dashboard'),
    url(r'^mepi/dashboard/recent$', 'recent_activity', name='recent_activity'),

    url(r'^mepi/dashboard/emergency_lab$', 'emergency_lab_dashboard', name='emergency_lab_dashboard'),

    url(r'^mepi/cases/(?P<case_id>[0-9a-fA-Z]{25,32})/$', 'view_case',  name='mepi_case'),
    url(r'^mepi/submission/(?P<doc_id>[0-9a-fA-Z]{25,32})$', 'show_submission', name='show_submission'),
    url(r'^exporter/$', 'csv_export_landing', name='csv_export_landing'),
    url(r'^exporter/file/$', 'export_excel_file', name='export_excel_file'),
    url(r'^exporter/cases/$', 'download_cases', name='download_cases'),
)