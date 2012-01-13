from django.conf.urls.defaults import *


#(r'^projects/(?P<project_id>\d+)/?$', 'buildmanager.views.show_project'),
urlpatterns = patterns ('careplan.views',
    url(r'^careplan/templates/all$', 'caretemplates.all_template_careplans', name='all_template_careplans'),
    (r'^careplan/templates/(?P<plan_id>[0-9a-f]{32})$', 'caretemplates.single_template_careplan'),

    (r'^careplan/templates/items/all$', 'caretemplates.all_template_items'),
    (r'^careplan/templates/items/(?P<item_id>[0-9a-f]{32})$', 'caretemplates.single_template_item'),

    url(r'^careplan/templates/new$', 'caretemplates.new_template_careplan', name='new_template_careplan'),
    url(r'^careplan/templates/items/new$', 'caretemplates.new_template_item', name='new_template_item'),

    url(r'^careplan/templates/items/new$', 'caretemplates.new_template_item', name='new_template_item'),
    url(r'^careplan/templates/(?P<plan_id>[0-9a-f]{32})/item/new$', 'caretemplates.add_new_item_to_template', name="add_new_item_to_template"),
    url(r'^careplan/templates/(?P<plan_id>[0-9a-f]{32})/item/add$', 'caretemplates.add_existing_item_to_template', name="add_existing_item_to_template"),
)
    
