from django.conf.urls.defaults import *

urlpatterns = patterns('dotsview.views', 
                       url(r'^dotsview/$', 'index_couch', name='dots_view'),
                       url(r'^dotsdebug/$', 'debug_case_dots', name='dots_debug'),
                       url(r'^dotsview/download$', 'get_csv', name="dots_csv_download"),
                       url(r'^dotsview/addendum$', 'dot_addendum', name="dot_addendum_dialog"),
                       url(r'^dotsview/addendum/rm$', 'delete_reconciliation', name="delete_addendum"),
                       url(r'^dotsview/download/(?P<download_id>[0-9a-fA-Z]{25,32})$', 'file_download'),
                        )