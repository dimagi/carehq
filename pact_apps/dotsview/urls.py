from django.conf.urls.defaults import *

urlpatterns = patterns('dotsview.views', 
                       url(r'^dotsview/$', 'index_couch', name='dots_view'),
                       url(r'^dotsview/download$', 'get_csv', name="dots_csv_download"),
                       url(r'^dotsview/addendum$', 'dot_addendum', name="dot_addendum_dialog"),
                       url(r'^dotsview/addendum/rm$', 'delete_reconciliation', name="delete_addendum"),
                        )