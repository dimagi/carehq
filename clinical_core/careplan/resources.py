from tastypie import fields
from tastypie.authorization import ReadOnlyAuthorization, DjangoAuthorization
from careplan.models import BaseCarePlan, BaseCarePlanItem, CarePlanInstance
from dimagi.utils.couch.tastykit import CouchdbkitResource, CouchdbkitTastyPaginator




class TemplateItemResource(CouchdbkitResource):
#    doc_id = fields.CharField(attribute='get_id')
#    last_name = fields.CharField(attribute='get_patient__last_name')
#    first_name = fields.CharField(attribute='get_patient__first_name')
#    formtype_display = fields.CharField(attribute='formtype_display')
#    start_time = fields.DateTimeField(attribute='start_date')
#    end_time = fields.DateTimeField(attribute='end_date')
#    finish_interval = fields.CharField(attribute='start_to_finish')
#    submit_interval = fields.CharField(attribute='finish_to_submit')
#    encounter_date = fields.CharField(attribute='encounter_date')
#    pact_id = fields.CharField(attribute='get_patient__pact_id')


    tenant = fields.CharField(attribute="tenant")
    title = fields.CharField(attribute='title')
    description = fields.CharField(attribute='description')
    #tags = StringListProperty()

    #created_by = StringProperty()
    #created_date = DateTimeProperty()

    #modified_by =  StringProperty()
    #modified_date = DateTimeProperty()

    class Meta:
        view_name = "careplan/template_items"
        doc_class = BaseCarePlanItem
        resource_name = 'TemplateItemResource'
        authorization = DjangoAuthorization()
        paginator_class=CouchdbkitTastyPaginator



class TemplateCarePlanResource(CouchdbkitResource):
#    doc_id = fields.CharField(attribute='get_id')
#    last_name = fields.CharField(attribute='get_patient__last_name')
#    first_name = fields.CharField(attribute='get_patient__first_name')
#    formtype_display = fields.CharField(attribute='formtype_display')
#    start_time = fields.DateTimeField(attribute='start_date')
#    end_time = fields.DateTimeField(attribute='end_date')
#    finish_interval = fields.CharField(attribute='start_to_finish')
#    submit_interval = fields.CharField(attribute='finish_to_submit')
#    encounter_date = fields.CharField(attribute='encounter_date')
#    pact_id = fields.CharField(attribute='get_patient__pact_id')

    doc_id = fields.CharField(attribute='get_id')
    tenant = fields.CharField(attribute='tenant')
    title = fields.CharField(attribute='title')
    description = fields.CharField(attribute='description')
    plan_items = fields.ListField(attribute='plan_items')

    tags = fields.ListField(attribute='tags')

    created_by = fields.CharField(attribute='created_by')
    created_date = fields.DateTimeField(attribute='created_date')

    modified_by =  fields.CharField(attribute='modified_by')
    modified_date = fields.DateTimeField(attribute='modified_date')


    class Meta:
        view_name = "careplan/template_careplans"
        doc_class = BaseCarePlan
        resource_name = 'TemplateCarePlanResource'
        authorization = DjangoAuthorization()
        paginator_class=CouchdbkitTastyPaginator



class CarePlanResource(CouchdbkitResource):
    doc_id = fields.CharField(attribute="get_id")
    title=fields.CharField(attribute='title')
    description = fields.CharField(attribute='description')
    patient_guid = fields.CharField(attribute='patient_guid')

    status = fields.CharField(attribute='status')

    tags = fields.ListField(attribute='tags')

    created_by = fields.CharField(attribute='created_by')
    created_date = fields.DateTimeField(attribute='created_date')

    modified_by =  fields.CharField(attribute='modified_by')
    modified_date = fields.DateTimeField(attribute='modified_date')


    class Meta:
        view_name = "careplan/by_patient"
        doc_class = CarePlanInstance
        resource_name = 'TemplateItemResource'
        authorization = DjangoAuthorization()
        paginator_class=CouchdbkitTastyPaginator



