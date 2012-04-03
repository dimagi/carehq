from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication, BasicAuthentication
from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.bundle import Bundle
from tastypie.constants import ALL_WITH_RELATIONS, ALL
from tastypie.fields import ForeignKey
from tastypie.resources import Resource, ModelResource
import restkit
from clinical_shared.utils.tastypie_utils import DatatablesModelResource
from couchforms.models import XFormInstance
from issuetracker.models.issuecore import Issue, IssueEvent
from patient.models import Patient
from permissions.models import Actor

class IssueEventResource(ModelResource):
    class Meta:
        queryset = IssueEvent.objects.all()
        authorization=ReadOnlyAuthorization()
        authentication=BasicAuthentication()
        resource_name='issueevent_api'

class PatientResource(ModelResource):
    class Meta:
        queryset = Patient.objects.all()
        authorization = ReadOnlyAuthorization()
        authentication=BasicAuthentication()
        resource_name='patient_api'

class ActorResource(ModelResource):
    class Meta:
        queryset = Actor.objects.all()
        authorization = ReadOnlyAuthorization()
        authentication=BasicAuthentication()
        resource_name='actor_api'

class IssueResource(DatatablesModelResource):
    opened_by = ForeignKey(ActorResource, 'opened_by')
    closed_by = ForeignKey(ActorResource, 'closed_by', null=True)
    resolved_by = ForeignKey(ActorResource, 'resolved_by', null=True)
    assigned_to = ForeignKey(ActorResource, 'assigned_to')
    last_edit_by = ForeignKey(ActorResource, 'last_edit_by')
    patient = ForeignKey(PatientResource, 'patient')

    opened_by_display=fields.CharField(readonly=True)
    last_edit_by_display =fields.CharField(readonly=True)

    last_event = ForeignKey(IssueEventResource, 'last_event')
    last_activity = fields.CharField('last_event__activity')

    def dehydrate_opened_by_display(self, bundle):
        if bundle.obj.opened_by is None:
            return ''
        else:
            return bundle.obj.opened_by.actordoc.get_name()
    def dehydrate_last_edit_by_display(self, bundle):
        if bundle.obj.last_edit_by is None:
            return ''
        else:
            return bundle.obj.last_edit_by.actordoc.get_name()



    class Meta:
        queryset = Issue.objects.all()
        resource_name='issue_api'
        authorization = ReadOnlyAuthorization()
        #authentication=ApiKeyAuthentication()
        authentication=BasicAuthentication()
        filtering = {
            'status': ALL,
            'category': ALL_WITH_RELATIONS,
            'user': ALL_WITH_RELATIONS,
            'patient': ALL_WITH_RELATIONS,

            'opened_by': ALL_WITH_RELATIONS,
            'assigned_to': ALL_WITH_RELATIONS,
            'last_edit_by': ALL_WITH_RELATIONS,
            'resolved_by': ALL_WITH_RELATIONS,
            'closed_by': ALL_WITH_RELATIONS,

            'parent_issue': ALL_WITH_RELATIONS,

            'priority': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
            'opened_date': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
            'assigned_date': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
            'resolved_date': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
            'closed_date': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
            'due_date': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
            }


#class IssueEventResource(ModelResource):
#    #printer = ForeignKey(ZebraPrinterResource, 'printer')
#    class Meta:
#        queryset = IssueEvent.objects.all()
#        resource_name='zebra_status'
#        authorization = Authorization()
#        authentication=ApiKeyAuthentication()





#class LabelResource(Resource):
#    # Just like a Django ``Form`` or ``Model``, we're defining all the
#    # fields we're going to handle with the API here.
#    uuid = fields.CharField(attribute='uuid')
#    case_guid = fields.CharField(attribute='case_guid')
#    destination_host = fields.CharField(attribute='dst_host')
#    destination_port = fields.CharField(attribute='dst_port')
#    zpl_code = fields.CharField(attribute='zpl')
#
#    class Meta:
#        resource_name = 'labelqueue'
#        object_class = XFormInstance
#        authorization = ReadOnlyAuthorization()
#
#    # Specific to this resource, just to get the needed Riak bits.
#    def _db(self):
#        return XFormInstance.get_db()
#
#    # The following methods will need overriding regardless of your
#    # data source.
#    def get_resource_uri(self, bundle_or_obj):
#        kwargs = {
#            'resource_name': self._meta.resource_name,
#        }
#
#        if isinstance(bundle_or_obj, Bundle):
#            kwargs['pk'] = bundle_or_obj.obj.uuid
#        else:
#            kwargs['pk'] = bundle_or_obj.uuid
#
#        if self._meta.api_name is not None:
#            kwargs['api_name'] = self._meta.api_name
#
#        return self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)
#
#    def get_object_list(self, request):
#        query = self._client().add('messages')
#        query.map("function(v) { var data = JSON.parse(v.values[0].data); return [[v.key, data]]; }")
#        results = []
#
#        for result in query.run():
#            new_obj = RiakObject(initial=result[1])
#            new_obj.uuid = result[0]
#            results.append(new_obj)
#
#        return results
#
#    def obj_get_list(self, request=None, **kwargs):
#        # Filtering disabled for brevity...
#        return self.get_object_list(request)
#
#    def obj_get(self, request=None, **kwargs):
#        bucket = self._bucket()
#        message = bucket.get(kwargs['pk'])
#        return RiakObject(initial=message.get_data())
#
#    def obj_create(self, bundle, request=None, **kwargs):
#        bundle.obj = RiakObject(initial=kwargs)
#        bundle = self.full_hydrate(bundle)
#        bucket = self._bucket()
#        new_message = bucket.new(bundle.obj.uuid, data=bundle.obj.to_dict())
#        new_message.store()
#        return bundle
#
#    def obj_update(self, bundle, request=None, **kwargs):
#        return self.obj_create(bundle, request, **kwargs)
#
#    def obj_delete_list(self, request=None, **kwargs):
#        bucket = self._bucket()
#
#        for key in bucket.get_keys():
#            obj = bucket.get(key)
#            obj.delete()
#
#    def obj_delete(self, request=None, **kwargs):
#        bucket = self._bucket()
#        obj = bucket.get(kwargs['pk'])
#        obj.delete()
#
#    def rollback(self, bundles):
#        pass