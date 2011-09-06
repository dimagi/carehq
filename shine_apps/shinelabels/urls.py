#URLS for your patient management should be managed by the app that subclasses the patient model.
from django.conf.urls.defaults import *
from shinelabels.api.resources import ZebraStatusResource, ZebraPrinterResource

status_resource = ZebraStatusResource()
printer_resource = ZebraPrinterResource()
urlpatterns = patterns('',
    (r'^api/', include(status_resource.urls)),
    (r'^api/', include(printer_resource.urls)),
)

