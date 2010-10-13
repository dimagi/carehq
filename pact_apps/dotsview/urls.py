from django.conf.urls.defaults import *

urlpatterns = patterns('dotsview.views',
    (r'^$', 'index'),
)