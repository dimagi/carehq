from django.conf.urls.defaults import *

urlpatterns = patterns('ashandui.views',
    url(r'^addProvider/?$', 'addProvider', name='addProvider'),
    url(r'^providerSearchAjax/?$', 'providerSearchAjax', name='providerSearchAjax'),
    url(r'^providerListQueryAjax/(?P<term>.*)$', 'providerListQueryAjax', name='providerListQueryAjax'),
    url(r'^providerSearch/?$', 'providerSearch', name='providerSearch'),
    url(r'^providerPatients/(?P<doctorId>[0-9a-f]{32})$', 'providerPatients'),
    url(r'^linkProvider/(?P<patientId>[0-9a-f]{32})?$', 'editCareteam', name='linkProvider'),
    url(r'^ashandHome/', 'ashandHome', name='ashandHome')
)
