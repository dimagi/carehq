#URLS for your patient management should be managed by the app that subclasses the patient model.

from django.conf.urls.defaults import *

urlpatterns = patterns('',
url(r'^patient/phone/rm$', 'patient.views.remove_phone', name='remove_phone'),
url(r'^patient/address/rm$', 'patient.views.remove_address', name='remove_address'),
)

