from django.conf.urls.defaults import *


#(r'^projects/(?P<project_id>\d+)/?$', 'buildmanager.views.show_project'),
urlpatterns = patterns ('',                        
    (r'^careplan/templates/all$', 'careplan.views.caretemplates.all_careplans'),    
    (r'^careplan/templates/(?P<plan_id>[0-9a-f]{32})$', 'careplan.views.caretemplates.single_careplan'),    
    (r'^careplan/templates/items/(?P<item_id>[0-9a-f]{32})$', 'careplan.views.caretemplates.single_careplan_item'),    
    (r'^careplan/templates/items/all$', 'careplan.views.caretemplates.all_careplan_items'),        
            
)    
    
