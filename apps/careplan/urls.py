from django.conf.urls.defaults import *

#(r'^projects/(?P<project_id>\d+)/?$', 'buildmanager.views.show_project'),
urlpatterns = patterns ('',
    (r'^template/items/$', 'careplan.views.all_template_items'),       
    (r'^templates/items/(?P<template_id>[0-9a-f]{32})$', 'careplan.views.view_template_item'),        
)    
    
