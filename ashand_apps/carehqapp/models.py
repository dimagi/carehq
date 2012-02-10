from couchdbkit.ext.django.schema import Document, BooleanProperty
from datetime import datetime
from couchforms.models import XFormInstance
from lxml import etree
from issuetracker.models.issuecore import ExternalIssueData, IssueCategory
from patient.models import BasePatient
import settings
import base64
import uuid

class UsabilitySurvey(Document):
    pass

def get_threshold_category():
    return IssueCategory.objects.get(id='040052ea2029408baf4583a78651635e')

def get_missing_category():
    return IssueCategory.objects.get(id='bddb8723084041238fdda8b37a1c0e35')

class CCDSubmission(XFormInstance):
    is_threshold = BooleanProperty()

    def save(self):
        #do nothing, this is just a wrapper
        pass

    def get_patient_guid(self):
        if len(self.form['recordTarget']['patientRole']['id']) > 2:
            b64_doc = self.form['recordTarget']['patientRole']['id'][2]['@extension']
            bytes = base64.b64decode(b64_doc)
            decoded_doc_id = uuid.UUID(bytes=bytes)
            return decoded_doc_id
            #return self.form['recordTarget']['patientRole']['id'][2]['@extension']
        else:
            return self.form['recordTarget']['patientRole']['id'][0]['@extension']

    def ccd_table_data(self):
        return CCDSubmission.find_ccd_table_data(self)

    @staticmethod
    def find_ccd_table_data(xform):
        attachment = xform.fetch_attachment('form.xml', stream=True)
        tree = etree.parse(attachment)
        r = tree.getroot()
        p = r.xpath('//hl7:component/hl7:structuredBody/hl7:component/hl7:section/hl7:text/hl7:table', namespaces={'hl7':'urn:hl7-org:v3'})
        table_fragment = etree.tostring(p[1])
        return table_fragment

    def get_session_time(self):
        return datetime.strptime(self.form['author']['time']['@value'][0:8], '%Y%m%d')

    def has_issue(self):
        if ExternalIssueData.objects.filter(doc_id = self._id).count() > 0:
            return True
        else:
            return False

    def get_issues(self):
         return Issue.objects.filter(external_data__doc_id = self._id)


    def get_patient_doc(self):
        #patient_doc_id = Patient.objects.get(doc_id=xform.form['recordTarget']['patientRole']['id'][1]['@extension'])
        #patient_doc_id = self.form['recordTarget']['patientRole']['id'][1]['@extension']
        #patient_doc = BasePatient.get_typed_from_dict(BasePatient.get_db().get(patient_doc_id))

        #hack for testing
        if hasattr(self, '_patient_doc'):
            return self._patient_doc

        try:
            patient = Patient.objects.get(doc_id=self.get_patient_guid())
            self._patient_doc = patient.couchdoc
            return patient.couchdoc
        except Patient.DoesNotExist:
            self._patient_doc = None
            return None


from signals import *
