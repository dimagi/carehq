from django.conf.urls.defaults import *
urlpatterns = patterns ('',
    url(r'^shine/callback/(?P<patient_id>[0-9a-fA-Z]{25,32})$', 'shineforms.views.touchforms_callback',
        name="shineforms_callback"),
    url(r'^shine/new/item_registration/(?P<patient_id>[0-9a-fA-Z]{25,32})$', 'shineforms.views.new_item_registration',
        name="new_item"),
    url(r'^shine/restore$', 'shineforms.views.ota_restore',
        name="shineforms_restore"),
    
)
