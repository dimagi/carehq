#URLS for your patient management should be managed by the app that subclasses the patient model.
from django.conf.urls.defaults import *
from shinelabels.api.resources import ZebraStatusResource, ZebraPrinterResource, LabelQueueResource

status_resource = ZebraStatusResource()
printer_resource = ZebraPrinterResource()
label_resource = LabelQueueResource()
label_resource = LabelQueueResource()
urlpatterns = patterns('',
    (r'^api/', include(status_resource.urls)),
    (r'^api/', include(printer_resource.urls)),
    (r'^api/', include(label_resource.urls)),
    url(r'^mepi/printlabel/(?P<patient_guid>[0-9a-fA-Z]{25,32})/$', 'shinelabels.views.print_jobs',  name='shinepatient_print_jobs'),

)

