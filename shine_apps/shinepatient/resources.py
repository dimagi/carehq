from tastypie import fields
from tastypie.authorization import Authorization
from dimagi.utils.couch.tastykit import CouchdbkitResource
from shinepatient.models import ShinePatient




class PatientDataResource(CouchdbkitResource):
    lab_data = fields.DictField(attribute='get_lab_data')
    bed = fields.CharField(attribute='get_current_bed')
    ward = fields.CharField(attribute='get_current_ward')

    class Meta:
        view_name = "shinepatient/shine_patients"
        doc_class = ShinePatient
        resource_name = 'ShinePatientData'
        authorization = Authorization()


class ShinePatientResource(CouchdbkitResource):
    first_name = fields.CharField(attribute=u'first_name')
    last_name = fields.CharField(attribute=u'last_name', null=True)
    gender = fields.CharField(attribute=u'gender', null=True)

    django_uuid = fields.CharField(attribute=u'django_uuid', null=True)
    cases = fields.ListField(attribute=u'cases', null=True)
    dob = fields.CharField(attribute=u'birthdate', null=True)
    date_modified = fields.CharField(attribute=u'date_modified', null=True)

    detail_uuid = fields.RelatedField(PatientDataResource, '_id')

    class Meta:
        view_name = "shinepatient/shine_patients"
        doc_class = ShinePatient
        resource_name = 'ShinePatient'
        authorization = Authorization()



