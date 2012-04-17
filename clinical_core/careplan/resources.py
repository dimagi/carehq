from django.conf.urls.defaults import url
from tastypie import fields
from tastypie.authorization import ReadOnlyAuthorization, DjangoAuthorization, Authorization
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
    def obj_get_list(self, request=None, **kwargs):
        """
        Assumes that the document type and the view correspond
        """
        #tune the limits for couch instead of grabbing everything

        results = self.call_view(request, **kwargs).all()
        return results

    def call_view(self, request, **kwargs):
        limit_option, skip_option = self._get_limit_skip(request)
        if request is not None and request.GET.get('current_actor', None) is not None:
            startkey = [request.current_actor.actor_tenant.tenant.name, {}]
            endkey = [request.current_actor.actor_tenant.tenant.name, None]
            view = self._meta.doc_class.view(self._meta.view_name, include_docs=True, startkey=startkey, endkey=endkey, limit=limit_option, descending=True)
        else:
            view = self._meta.doc_class.view(self._meta.view_name, include_docs=True, skip=skip_option, limit=limit_option, descending=True)
        return view

    class Meta:
        view_name = "careplan/template_careplans"
        doc_class = BaseCarePlan
        resource_name = 'TemplateCarePlanResource'
        authorization = Authorization()
        #authorization = DjangoAuthorization()
        paginator_class=CouchdbkitTastyPaginator
        object_class = BaseCarePlan



class CarePlanResource(CouchdbkitResource):
    doc_id = fields.CharField(attribute="get_id")
    rev = fields.CharField(attribute="_rev")
    title=fields.CharField(attribute='title')
    description = fields.CharField(attribute='description')
    patient_guid = fields.CharField(attribute='patient_guid')

    status = fields.CharField(attribute='status')

    tags = fields.ListField(attribute='tags')

    created_by = fields.CharField(attribute='created_by')
    created_date = fields.DateTimeField(attribute='created_date')

    modified_by =  fields.CharField(attribute='modified_by')
    modified_date = fields.DateTimeField(attribute='modified_date')

    def obj_get_list(self, request=None, **kwargs):
        """
        Assumes that the document type and the view correspond
        """
        #tune the limits for couch instead of grabbing everything

        results = self.call_view(request, **kwargs).all()
        return results

    def call_view(self, request, **kwargs):
        limit_option, skip_option = self._get_limit_skip(request)

        if request is not None and kwargs.get('patient_guid', None) is not None:
            key = kwargs['patient_guid']
            view = self._meta.doc_class.view(self._meta.view_name, include_docs=True, key=key, limit=limit_option, descending=True)
        else:
            view = self._meta.doc_class.view(self._meta.view_name, include_docs=True, skip=skip_option, limit=limit_option, descending=True)
        return view

    def override_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/(?P<patient_guid>.*)/' % self._meta.resource_name, self.wrap_view('dispatch_list'), name='api_careplan_by_pact_id'),
        ]

    class Meta:
        view_name = "careplan/by_patient"
        doc_class = CarePlanInstance
        resource_name = 'patient_care_plan'
        authorization = DjangoAuthorization()
        paginator_class=CouchdbkitTastyPaginator




