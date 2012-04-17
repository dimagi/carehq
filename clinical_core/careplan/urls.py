from django.conf.urls.defaults import *
from careplan.resources import TemplateCarePlanResource, TemplateItemResource, CarePlanResource

template_plan_resource = TemplateCarePlanResource()
template_item_resource = TemplateItemResource()
careplan_resource = CarePlanResource()
#(r'^projects/(?P<project_id>\d+)/?$', 'buildmanager.views.show_project'),
urlpatterns = patterns ('careplan.views',

    (r'^careplan/api/', include(template_plan_resource.urls)),
    (r'^careplan/api/', include(template_item_resource.urls)),
    (r'^careplan/api/', include(careplan_resource.urls)),

    url(r'^careplan/templates/all$', 'caretemplates.all_template_careplans', name='all_template_careplans'),
    (r'^careplan/templates/(?P<plan_id>[0-9a-f]{32})$', 'caretemplates.single_template_careplan'),

    (r'^careplan/templates/items/all$', 'caretemplates.all_template_items'),
    (r'^careplan/templates/items/(?P<item_id>[0-9a-f]{32})$', 'caretemplates.single_template_item'),

    url(r'^careplan/templates/new$', 'caretemplates.new_template_careplan', name='new_template_careplan'),
    url(r'^careplan/templates/items/new$', 'caretemplates.new_template_item', name='new_template_item'),

    url(r'^careplan/templates/items/new$', 'caretemplates.new_template_item', name='new_template_item'),
    url(r'^careplan/templates/(?P<plan_id>[0-9a-f]{32})/item/new$', 'caretemplates.add_new_item_to_template', name="add_new_item_to_template"),
    url(r'^careplan/templates/(?P<plan_id>[0-9a-f]{32})/item/add$', 'caretemplates.add_existing_item_to_template', name="add_existing_item_to_template"),


    url(r'^careplan/templates/link$', 'planinstances.link_template_careplan_for_patient', name="link_template_careplan_for_patient"),

    url(r'^careplan/patient/(?P<patient_guid>[0-9a-f]{32})$', 'planinstances.manage_patient_careplan', name="manage_patient_careplan"),
    url(r'^careplan/patient/(?P<patient_guid>[0-9a-f]{32})/(?P<plan_id>[0-9a-f]{32})$', 'planinstances.new_patient_careplan_item', name="new_patient_careplan_item"),

)
    
