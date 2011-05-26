from django.conf.urls.defaults import *
from django.conf import settings

#(r'^projects/(?P<project_id>\d+)/?$', 'buildmanager.views.show_project'),
urlpatterns = patterns('',
                       (r'^slideforms$', 'slidesview.views.all_slideforms'),
                       (r'^slideforms/(?P<doc_id>[0-9a-fA-Z]{25,32})$', 'slidesview.views.slideform'),
                       (r'^imgproxy/(?P<doc_id>[0-9a-fA-Z]{25,32})/(?P<attachment_key>.*)$', 'slidesview.views.image_proxy'),
                       )

