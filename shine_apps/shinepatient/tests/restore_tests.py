import base64
import uuid
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from quicksect import IntervalNode
from datetime import datetime, timedelta
import re
from casexml.apps.case.models import CommCareCase
from receiver.util import spoof_submission
from shineforms.models import ShineUser
from shinepatient.models import ShinePatient
from django.test.client import Client
from django_digest.test import Client as DigestClient

create_patient_xml = """
<data xmlns:jrm="http://dev.commcarehq.org/jr/xforms" xmlns="http://shine.commcarehq.org/patient/reg" uiVersion="2" version="1">
  <Meta>
    <DeviceID>touchforms</DeviceID>
    <TimeStart>2011-07-05T22:27:52.885-04</TimeStart>
    <TimeEnd>2011-07-05T22:28:00.045-04</TimeEnd>
    <username>admin</username>
    <chw_id>2</chw_id>
    <uid>%(uid)s</uid>
  </Meta>
  <case>
    <case_id>%(case_id)s</case_id>
    <date_modified>2011-07-05T22:28:00.045-04</date_modified>
    <create>
      <case_type_id>shine_patient</case_type_id>
      <user_id>2</user_id>
      <case_name>%(last_name)s, %(first_name)s</case_name>
      <external_id>%(external_id)s</external_id>
    </create>
    <update>
      <patient_guid>%(patient_guid)s</patient_guid>
      <first_name>%(first_name)s</first_name>
      <last_name>%(last_name)s</last_name>
      <sex>male</sex>
      <dob>2011-07-01</dob>
    </update>
  </case>
  <generated/>
</data>
"""

#http auth with django client, source: http://stackoverflow.com/questions/6068674/django-test-client-http-basic-auth-for-post-request
def http_auth(username, password):
    credentials = base64.encodestring('%s:%s' % (username, password)).strip()
    auth_string = 'Basic %s' % credentials
    return auth_string

class ShinePatientRestoreTests(TestCase):
    def setUp(self):
        User.objects.all().delete()
        self.user = self._createUser()
        self.extra = {
            'HTTP_AUTHORIZATION': http_auth('mockmock@mockmock.com', 'mockmock')
        }


    def _createUser(self):
        usr = User()
        usr.username = 'mockmock@mockmock.com'
        usr.set_password('mockmock')
        usr.first_name='mocky'
        usr.last_name = 'mock'
        usr.save()
        return usr

    def _mkpatient_dict(self):
        data_dict = {}

        data_dict['uid'] = uuid.uuid4().hex
        data_dict['case_id'] = uuid.uuid4().hex
        data_dict['patient_guid'] = uuid.uuid4().hex
        data_dict['external_id'] = "mockexternalid"
        data_dict['first_name'] = "mockfirstname"
        data_dict['last_name'] = "mockfirstname"
        return data_dict

    def testCreatePatient(self):
        """
        Ensure that a submitted patient registration xml file creates ShinePatient object and Case object.
        """
        pdict = self._mkpatient_dict()
        xml = create_patient_xml % pdict
        resp = spoof_submission(reverse("receiver_post"), xml, hqsubmission=False)

        shinept = ShinePatient.get(pdict['patient_guid'])
        self.assertEqual(shinept['external_id'], pdict['external_id'])

        casedoc=CommCareCase.get(pdict['case_id'])
        self.assertEqual(casedoc['first_name'], pdict['first_name'])
        self.assertEqual(casedoc['last_name'], pdict['last_name'])
        self.assertEqual(casedoc['patient_guid'], pdict['patient_guid'])
        self.assertEqual(casedoc['external_id'], pdict['external_id'])
        return shinept, casedoc

    def testRestore(self):
        """For a given patient created, ensure that it shows up in the OTA restore.  This test also uses django_digest to authenticate to the OTA restore URL.
        """
        pt, casedoc = self.testCreatePatient()


        shineuser = ShineUser.from_django_user(self.user)

        client = DigestClient()
        client.set_authorization(self.user.username, 'mockmock', 'Digest')
        restore_payload = client.get('/shine/restore', **self.extra)

        case_id_re = re.compile('<case_id>(?P<case_id>\w+)<\/case_id>')
        case_id_xml = case_id_re.search(restore_payload.content).group('case_id')
        self.assertEqual(case_id_xml, casedoc._id)



