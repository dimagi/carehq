import base64
import pdb
import uuid
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.test import TestCase
from django_webtest import WebTest
from quicksect import IntervalNode
from datetime import datetime, timedelta
import os
import random
import re
from casexml.apps.case.models import CommCareCase
from shineforms.models import ShineUser
from shinepatient.models import ShinePatient
from django.test.client import Client
from django_digest.test import Client as DigestClient
from StringIO import StringIO
from couchforms.models import XFormInstance
from shinepatient.tests.testutils import _mkpatient_dict, get_registration_xml, do_submit, create_image
from hutch.models import AttachmentImage


image_submit_xml = """
<data xmlns:jrm="http://dev.commcarehq.org/jr/xforms" xmlns="http://shine.commcarehq.org/bloodwork/entry" uiVersion="1" version="1">
  <Meta>
    <DeviceID>354957030960291</DeviceID>
    <TimeStart>2011-07-07T19:28:50.531-04</TimeStart>
    <TimeEnd>2011-07-07T19:29:12.806-04</TimeEnd>
    <username>shine</username>
    <chw_id>2</chw_id>
    <uid>%(uid)s</uid>
  </Meta>
  <case>
    <case_id>%(case_id)s</case_id>
    <date_modified>2011-07-07T19:29:12.806-04</date_modified>
    <update>
      <performed>Yes</performed>
      <image tag="attachment">testimage.jpg</image>
      <result>positive</result>
    </update>
    <close/>
  </case>
  <performed>Yes</performed>
  <outcome>
    <image>testimage.jpg</image>
    <result>positive</result>
  </outcome>
</data>
"""



generated_image_xml = """
<data xmlns:jrm="http://dev.commcarehq.org/jr/xforms" xmlns="http://shine.commcarehq.org/bloodwork/entry" uiVersion="1" version="1">
  <Meta>
    <DeviceID>354957030960291</DeviceID>
    <TimeStart>%(timestart)s</TimeStart>
    <TimeEnd>%(timeend)s</TimeEnd>
    <username>shine</username>
    <chw_id>2</chw_id>
    <uid>%(uid)s</uid>
  </Meta>
  <case>
    <case_id>%(case_id)s</case_id>
    <date_modified>%(datemodified)s</date_modified>
    <update>
      <performed>Yes</performed>
      <image tag="attachment">%(imagename)s</image>
      <result>positive</result>
    </update>
    <close/>
  </case>
  <performed>Yes</performed>
  <outcome>
    <image>%(imagename)s</image>
    <result>%(result)s</result>
  </outcome>
</data>
"""



#http auth with django client, source: http://stackoverflow.com/questions/6068674/django-test-client-http-basic-auth-for-post-request
def http_auth(username, password):
    credentials = base64.encodestring('%s:%s' % (username, password)).strip()
    auth_string = 'Basic %s' % credentials
    return auth_string


class ShinePatientTests(TestCase):
    def setUp(self):
        User.objects.all().delete()
        self.user = self._createUser()
        self.extra = {
            'HTTP_AUTHORIZATION': http_auth('mockmock@mockmock.com', 'mockmock')
        }

    def tearDown(self):
        if hasattr(self, 'patient') and self.patient != None:
            self.patient.delete()
        if hasattr(self, 'casedoc') and self.casedoc != None:
            self.casedoc.delete()

    def _createUser(self):
        usr = User()
        usr.username = 'mockmock@mockmock.com'
        usr.set_password('mockmock')
        usr.first_name = 'mocky'
        usr.last_name = 'mock'
        usr.save()
        return usr


    def testCreatePatient(self):
        """
        Ensure that a submitted patient registration xml file creates ShinePatient object and Case object.
        """
        pdict = _mkpatient_dict()
        final_xml = get_registration_xml(pdict)

        consent_image = create_image(100,100,"Consent Form!")

        do_submit(final_xml, attachments_list=[('consent.jpg', consent_image)])

        shinept = ShinePatient.view('shinepatient/patient_cases_all', key=pdict['case_id'], include_docs=True).first()
        self.assertEqual(shinept['external_id'], str(pdict['external_id']))

        casedoc = CommCareCase.get(pdict['case_id'])
        self.assertEqual(casedoc['first_name'], pdict['first_name'])
        self.assertEqual(casedoc['last_name'], pdict['last_name'])
        self.assertEqual(casedoc['external_id'], str(pdict['external_id']))

        self.patient = shinept
        self.casedoc = casedoc


    def testRegisterPatients(self):
        """
        Ensure that a submitted patient registration xml file creates ShinePatient object and Case object.
        """
        for x in range(0,10):
            pdict = _mkpatient_dict()
            case_id = pdict['case_id']
            final_xml = get_registration_xml(pdict)
            consent_image = create_image(100,100,"Consent Form!")
            do_submit(final_xml, attachments_list=[('consent.jpg', consent_image)])

            patient_doc = ShinePatient.view('shinepatient/patient_cases_all', include_docs=True, key=case_id).first()

            client = Client()
            client.login(username=self.user.username, password='mockmock')
            dashboard = client.get("/")
            client.logout()
            self.assertTrue(dashboard.content.count(pdict['last_name']) > 0)
            self.assertTrue(dashboard.content.count(patient_doc._id) > 0)


            #see ota as well:
            client = DigestClient()
            client.set_authorization(self.user.username, 'mockmock', 'Digest')
            restore_payload = client.get('/shine/restore', **self.extra)
            self.assertEqual(restore_payload.content.count(case_id), 1)
            #case_id_re = re.compile('<case_id>(?P<case_id>\w+)<\/case_id>')
            #case_id_xml = case_id_re.search(restore_payload.content).group('case_id')
            #pdb.set_trace()
            #self.assertEqual(case_id_xml, case_id)





    def testRestore(self):
        """For a given patient created, ensure that it shows up in the OTA restore.  This test also uses django_digest to authenticate to the OTA restore URL.
        """
        self.testCreatePatient()

        shineuser = ShineUser.from_django_user(self.user)

        client = DigestClient()
        client.set_authorization(self.user.username, 'mockmock', 'Digest')
        restore_payload = client.get('/shine/restore', **self.extra)
        case_id_re = re.compile('<case_id>(?P<case_id>\w+)<\/case_id>')
        case_id_xml = case_id_re.search(restore_payload.content).group('case_id')
        self.assertEqual(case_id_xml, self.casedoc._id)


    def testSubmitImages(self):
        self.testCreatePatient()
        client = Client()
        testimage = 'testimage.jpg'

        uid = uuid.uuid1().hex
        case_id = uuid.uuid1().hex
        final_xml = image_submit_xml % ({'uid': uid, 'case_id': case_id})

        xml_f = StringIO(final_xml.encode('utf-8'))
        xml_f.name = 'form.xml'

        image_f = open(os.path.join(os.path.dirname(__file__), 'testdata/%s' % testimage), 'rb')

        response = client.post(reverse('receiver_post'), {
            'xml_submission_file': xml_f,
            testimage: image_f,
            })

        try:
            xform = XFormInstance.get(uid)
        except Exception, ex:
            self.fail("Error, submission not retrieved: %s" % ex)

        images = AttachmentImage.objects.filter(doc_id=uid, attachment_key=testimage)
        self.assertEqual(len(images), 1)

    def _random_td(self):
        return timedelta(days=random.randint(0,365))

    def testSubmitAttachments(self):
        #self.testCreatePatient()

        for x in range(1,5):
            print "Creating and submitting image %d" % (x)
            #generate image
            #attach and submit
            #verify image exists.

            startdate = datetime.utcnow() - self._random_td()

            uid = uuid.uuid1().hex
            case_id = uuid.uuid1().hex

            submit_dict = {}
            submit_dict['uid'] = uid
            submit_dict['case_id'] = case_id
            submit_dict['timestart'] = startdate.strftime("%Y-%m-%dT%H:%M:%SZ")
            submit_dict['timeend'] = (startdate + timedelta(seconds=random.randint(1,1000))).strftime("%Y-%m-%dT%H:%M:%SZ")

            submit_dict['datemodified'] = startdate.strftime("%Y-%m-%dT%H:%M:%SZ")
            submit_dict['result'] = random.choice(['positive', 'negative','inconclusive'])

            filename = uuid.uuid1().hex + ".jpg"
            submit_dict['imagename'] = filename


            final_xml = generated_image_xml % (submit_dict)
            xml_f = StringIO(final_xml.encode('utf-8'))
            xml_f.name = 'form.xml'

            image_f = create_image(x*100, x*100, x )
            image_f.name = filename

            client = Client()
            response = client.post(reverse('receiver_post'), {
                'xml_submission_file': xml_f,
                filename: image_f,
                })

            try:
                xform = XFormInstance.get(uid)
                self.assertTrue(xform._attachments.has_key(filename))
            except Exception, ex:
                self.fail("Error, submission not retrieved: %s" % ex)


            #images = AttachmentImage.objects.filter(xform_id=uid, attachment_key=filename)
            #self.assertEqual(len(images), 1)






