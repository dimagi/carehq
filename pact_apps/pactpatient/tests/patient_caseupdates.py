from StringIO import StringIO
import uuid
import re
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from datetime import  datetime
import random
from couchforms.models import XFormInstance
from patient.models import CAddress
from pactpatient.caseconvert import set_cphones_to_case
from casexml.apps.case.models import CommCareCase
from patient.models import CPhone
from pactpatient.models import PactPatient
from patient.models import Patient
from .pactpatient_test_utils import delete_all
from pactcarehq.scripts.scrambler import make_random_cphone, make_random_caddress
from pactpatient.updater import generate_update_xml_old
import receiver.views as receiver_views

from django_digest.test import Client as DigestClient

class patientCaseUpdateTests(TestCase):
    NUM_PHONES=5
    NUM_ADDRESSES = 2


    def setUp(self):
        User.objects.all().delete()
        Patient.objects.all().delete()
        delete_all(PactPatient, 'patient/all')
        self.client = Client()
        self._createUser()

    def _createUser(self):
        self.user = User()
        self.user.username = 'mockmock@mockmock.com'
        self.user.set_password('mockmock')
        self.user.first_name='mocky'
        self.user.last_name = 'mock'
        self.user.save()

    def testOTARestore(self):
        """
        For a given patient created, ensure that it shows up in the OTA restore.
        Ensure also that changes in phone and addresses also show up in OTA restore.
        This test also uses django_digest to authenticate to the OTA restore URL.


        Verify all the phone and address information
        """
        patient_doc = self.test0CreatePatient()

        client = DigestClient()
        client.set_authorization(self.user.username, 'mockmock', 'Digest')
        restore_payload = client.get('/provider/caselist')

        case_id_re = re.compile('<case_id>(?P<case_id>\w+)<\/case_id>')
        case_id_xml = case_id_re.search(restore_payload.content).group('case_id')

        casedoc = CommCareCase.get(patient_doc.case_id)
        
        self.assertEqual(case_id_xml, casedoc._id)

    def test3PushPhonesIteratively(self):
        """
        Check to see if transactional single updates can do it vs. doing all each time
        """
        patient_doc = self.test0CreatePatient()
        allphones = []
        addresses = []
        for n in range(0,self.NUM_PHONES):
            newphone = make_random_cphone()
            newphone.description += "%s" % str(n+1)
            allphones.append(newphone)

            to_send = [None for q in range(0,n)]
            to_send.append(newphone)

            #now, submit the xml.
            xml_body = generate_update_xml_old(User.objects.all()[0], patient_doc, to_send, addresses)
            xml_stream = StringIO(xml_body.encode('utf-8'))
            xml_stream.name = "xml_submission_file"

            uid_re = re.compile('<uid>(?P<doc_id>\w+)<\/uid>')
            submit_doc_id = uid_re.search(xml_body).group('doc_id')
            response = self.client.post(reverse('receiver.views.post'), {'xml_submission_file': xml_stream })

            #verify submission worked
            try:
                XFormInstance.get(submit_doc_id)
            except:
                self.fail("XForm submit failed")

            #verify casexml updated
            casedoc_updated = CommCareCase.get(patient_doc.case_id)

            for i, p in enumerate(allphones, start=1):
                self.assertTrue(hasattr(casedoc_updated, 'Phone%d' % i))
                self.assertEquals(p.number, getattr(casedoc_updated,'Phone%d' % i))
                self.assertEquals(p.description, getattr(casedoc_updated,'Phone%dType' % i))
                self.assertTrue(hasattr(casedoc_updated, 'Phone%dType' % i))



    def test2PushNewPhone(self):
        """
        Verify on the webform that the display is showing up on the patient view.
        """
        patient, phones, addresses = self.test1CreatePatientVerifyAddressAPI()
        response = self.client.post('/accounts/login/', {'username': 'mockmock@mockmock.com', 'password': 'mockmock'})

        response = self.client.get(reverse('view_pactpatient', kwargs={'patient_guid': patient._id}))
        content = response.content

        phone_indices = []
        for p in phones:
            #make sure the numbers are in the right order
            phone_indices.append(content.index(p.number))
        self.assertEquals(sorted(phone_indices), phone_indices)




    def test1CreatePatientVerifyAddressAPI(self):
        """
        Test create phone and addresses, submit via casexml and verify casexml gets updated with latest from patient model.
        This does it via API
        """
        patient_doc = self.test0CreatePatient()
        phones = []
        addresses = []
        for n in range(0,self.NUM_PHONES):
            newphone = make_random_cphone()
            newphone.description += "%s" % str(n+1)
            phones.append(newphone)
        for n in range(0, self.NUM_ADDRESSES):
            newaddress = make_random_caddress()
            newaddress.description += "%s" % str(n+1)
            addresses.append(newaddress)
        patient_doc.save()
        #first verify that the case got nothing
        casedoc_blank = CommCareCase.get(patient_doc.case_id)
        for n in range(1, self.NUM_PHONES+1):
            self.assertFalse(hasattr(casedoc_blank, 'Phone%d' % n))
            self.assertFalse(hasattr(casedoc_blank, 'Phone%dType' % n))

        for n in range(1, self.NUM_ADDRESSES + 1):
            self.assertFalse(hasattr(casedoc_blank, 'address%d' % n))
            self.assertFalse(hasattr(casedoc_blank, 'address%dtype' % n))


        #now, submit the xml.
        xml_body = generate_update_xml_old(User.objects.all()[0], patient_doc, phones, addresses)
        xml_stream = StringIO(xml_body.encode('utf-8'))
        xml_stream.name = "xml_submission_file"

        uid_re = re.compile('<uid>(?P<doc_id>\w+)<\/uid>')
        submit_doc_id = uid_re.search(xml_body).group('doc_id')
        response = self.client.post(reverse('receiver.views.post'), {'xml_submission_file': xml_stream })

        #verify submission worked
        try:
            XFormInstance.get(submit_doc_id)
        except:
            self.fail("XForm submit failed")

        #verify casexml updated

        casedoc_updated = CommCareCase.get(patient_doc.case_id)

        for n in range(1, self.NUM_PHONES+1):
            p = phones[n-1]
            self.assertTrue(hasattr(casedoc_updated, 'Phone%d' % n))

            self.assertEquals(p.number, getattr(casedoc_updated,'Phone%d' % n))
            self.assertEquals(p.description, getattr(casedoc_updated,'Phone%dType' % n))

            self.assertTrue(hasattr(casedoc_updated, 'Phone%dType' % n))
        for n in range(1, self.NUM_ADDRESSES + 1):
            address = addresses[n-1]
            self.assertTrue(hasattr(casedoc_updated, 'address%d' % n))
            self.assertTrue(hasattr(casedoc_updated, 'address%dtype' % n))
            self.assertEquals(address.description, getattr(casedoc_updated,'address%dtype' % n))


        return patient_doc, phones, addresses

    def test0CreatePatient(self):
        """
        Test creates new patients and verify casexml is made alongside them
        Returns a patient couchdoc.
        """
        response = self.client.post('/accounts/login/', {'username': 'mockmock@mockmock.com', 'password': 'mockmock'})
        response = self.client.post('/patient/new', {'first_name':'foo',
                                                      'last_name': 'bar',
                                                      'gender':'m',
                                                      'birthdate': '1/1/2000',
                                                      'pact_id': 'mockmock',
                                                      'arm': 'DOT',
                                                      'art_regimen': 'QD',
                                                      'non_art_regimen': 'BID',
                                                      'primary_hp': 'isaac',
                                                      'patient_id': uuid.uuid4().hex,
                                                      'race': 'asian',
                                                      'is_latino': 'yes',
                                                      'mass_health_expiration': '1/1/2020',
                                                      'hiv_care_clinic': 'brigham_and_womens_hospital',
                                                      'ssn': '1112223333',
                                                      'preferred_language': 'english',
#                                                      'notes': 'foo'
                                                    })
#        f = open('response.html', 'w')
#        f.write(response.content)
#        f.close()
        self.assertEquals(response.status_code, 302) #if it's successful, then it'll do a redirect.
        self.assertEqual(1, Patient.objects.all().count())
        patient = Patient.objects.all()[0]

        casedoc = CommCareCase.get(patient.couchdoc.case_id)
        self.assertEquals(casedoc.external_id, patient.couchdoc.pact_id)
        return patient.couchdoc



        #start pushing xml submissions via form
        #verify that they get updated on casexml
        #verify on website that those phone numbers appear with client view..




        #setup phone numbers using old style


