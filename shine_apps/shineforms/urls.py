from django.conf.urls.defaults import *
urlpatterns = patterns ('',
    url(r'^shine/callback/(?P<patient_guid>[0-9a-fA-Z]{25,32})$', 'shineforms.views.new_bloodwork_order_cb',
        name="new_bloodwork_order_cb"),
    url(r'^shine/new/bw_order/(?P<patient_guid>[0-9a-fA-Z]{25,32})$', 'shineforms.views.new_bloodwork_order',
        name="new_bloodwork_order"),
    url(r'^shine/restore$', 'shineforms.views.ota_restore',
        name="shineforms_restore"),
    
)
