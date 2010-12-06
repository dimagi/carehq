from django.conf.urls.defaults import *

urlpatterns = patterns('dotsview.views', 
                       (r'^dotsview/sql$', 'index'),
                       url(r'^dotsview/$', 'index_couch', name='dots_view'),
                       url(r'^dotsview/download$', 'get_csv', name="dots_csv_download"),
                        )