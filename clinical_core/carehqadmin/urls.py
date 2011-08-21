from django.conf.urls.defaults import *

urlpatterns = patterns('carehqadmin.views',
    url(r'^carehqadmin/$', 'landing', name='carehqadmin_landing'),


    url(r'^carehqadmin/landlord$', 'landlord.landing', name='landlord_landing'),
    url(r'^carehqadmin/tenant/(?P<tenant_id>[0-9a-fA-Z]{25,32})$', 'tenants.manage_tenant', name='manage_tenant'),
    url(r'^carehqadmin/tenant/(?P<tenant_id>[0-9a-fA-Z]{25,32})/actor/new$', 'actors.new_actor', name='new_actor'),




#    url(r'^carehqadmin/providers$', 'all_pact_providers', name='all_pact_providers'),
#    url(r'^carehqadmin/providers/new$', 'new_pact_provider', name='new_pact_provider'),
)
