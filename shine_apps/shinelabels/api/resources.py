from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.bundle import Bundle
from tastypie.fields import ForeignKey
from tastypie.resources import Resource, ModelResource
import restkit
from couchforms.models import XFormInstance
from shinelabels.models import ZebraPrinter, LabelQueue, ZebraStatus

class ZebraPrinterResource(ModelResource):
    class Meta:
        queryset = ZebraPrinter.objects.all()
        resource_name='zebra_printers'
        authorization = ReadOnlyAuthorization()
        authentication=ApiKeyAuthentication()

class ZebraStatusResource(ModelResource):
    printer = ForeignKey(ZebraPrinterResource, 'printer')
    class Meta:
        queryset = ZebraStatus.objects.all()
        resource_name='zebra_status'
        authorization = Authorization()
        authentication=ApiKeyAuthentication()

class LabelQueueResource(ModelResource):
    destination_printer = ForeignKey(ZebraPrinterResource, 'destination')
    class Meta:
        queryset = LabelQueue.objects.all().filter(fulfilled_date=None)
        authorization = Authorization()
        authentication=ApiKeyAuthentication()
        resource_name='zebra_queue'



class LabelResource(Resource):
    # Just like a Django ``Form`` or ``Model``, we're defining all the
    # fields we're going to handle with the API here.
    uuid = fields.CharField(attribute='uuid')
    case_guid = fields.CharField(attribute='case_guid')
    destination_host = fields.CharField(attribute='dst_host')
    destination_port = fields.CharField(attribute='dst_port')
    zpl_code = fields.CharField(attribute='zpl')

    class Meta:
        resource_name = 'labelqueue'
        object_class = XFormInstance
        authorization = ReadOnlyAuthorization()

    # Specific to this resource, just to get the needed Riak bits.
    def _db(self):
        return XFormInstance.get_db()

    # The following methods will need overriding regardless of your
    # data source.
    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.uuid
        else:
            kwargs['pk'] = bundle_or_obj.uuid

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)

    def get_object_list(self, request):
        query = self._client().add('messages')
        query.map("function(v) { var data = JSON.parse(v.values[0].data); return [[v.key, data]]; }")
        results = []

        for result in query.run():
            new_obj = RiakObject(initial=result[1])
            new_obj.uuid = result[0]
            results.append(new_obj)

        return results

    def obj_get_list(self, request=None, **kwargs):
        # Filtering disabled for brevity...
        return self.get_object_list(request)

    def obj_get(self, request=None, **kwargs):
        bucket = self._bucket()
        message = bucket.get(kwargs['pk'])
        return RiakObject(initial=message.get_data())

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj = RiakObject(initial=kwargs)
        bundle = self.full_hydrate(bundle)
        bucket = self._bucket()
        new_message = bucket.new(bundle.obj.uuid, data=bundle.obj.to_dict())
        new_message.store()
        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        return self.obj_create(bundle, request, **kwargs)

    def obj_delete_list(self, request=None, **kwargs):
        bucket = self._bucket()

        for key in bucket.get_keys():
            obj = bucket.get(key)
            obj.delete()

    def obj_delete(self, request=None, **kwargs):
        bucket = self._bucket()
        obj = bucket.get(kwargs['pk'])
        obj.delete()

    def rollback(self, bundles):
        pass