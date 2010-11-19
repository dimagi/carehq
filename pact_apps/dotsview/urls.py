from django.conf.urls.defaults import *

urlpatterns = patterns('dotsview.views', 
                       (r'^sql$', 'index'),
                       url(r'^$', 'index_couch', name='dots_view'),
                       url(r'^download$', 'get_csv', name="dots_csv_download"),
                        )