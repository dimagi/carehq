from django.conf.urls.defaults import *

urlpatterns = patterns('dotsview.views', 
                       (r'^sql$', 'index'),
                       (r'^$', 'index_couch'),
                       url(r'^download$', 'get_csv', name="dots_csv_download"),
                        )