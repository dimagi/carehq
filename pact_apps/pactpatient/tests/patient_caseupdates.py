from StringIO import StringIO
import pdb
import random
import uuid
from django.contrib.sessions.backends.file import SessionStore
from django.core.management import call_command
import re
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from clinical_shared.tests.testcase import CareHQClinicalTestCase
from clinical_shared.utils import generator
from clinical_shared.utils.scrambler import make_random_cphone, make_random_caddress
from couchforms.models import XFormInstance
from casexml.apps.case.models import CommCareCase
from dimagi.utils.printing import print_pretty_xml
from pactpatient import caseapi
from pactpatient.enums import PACT_HIV_CLINIC_CHOICES
from pactpatient.forms.patient_form import PactPatientForm
from pactpatient.models import PactPatient
from pactpatient.views import new_patient
from patient.models import Patient
from .pactpatient_test_utils import delete_all
from pactpatient.updater import generate_update_xml_old

from django_digest.test import Client as DigestClient
from permissions.models import Actor, Role, PrincipalRoleRelation
from permissions.tests import RequestFactory
from tenant.models import Tenant
from django.core.cache import cache

class patientCaseUpdateTests(CareHQClinicalTestCase):
    """
    Tests for existing hacked OTA restore case
    """
    NUM_PHONES = 5
    NUM_ADDRESSES = 2


    def setUp(self):
        User.objects.all().delete()
        Actor.objects.all().delete()
        Role.objects.all().delete()
        PrincipalRoleRelation.objects.all().delete()
        delete_all(PactPatient, 'patient/all')
        call_command('carehq_init')
        self.tenant = Tenant.objects.all()[0]
        self._createUser()
        self.client = Client()
        cache.clear()

    def _doOTARestore(self):
        cache.clear()
        client = DigestClient()
        client.set_authorization(self.user.username, 'mockmock', 'Digest')
        restore_payload = client.get('/restore/')
        return restore_payload



    def testOTARestore(self):
        """
        For a given patient created, ensure that it shows up in the OTA restore.
        Ensure also that changes in phone and addresses also show up in OTA restore.
        This test also uses django_digest to authenticate to the OTA restore URL.


        Verify all the phone and address information
        """
        patient_doc = self.test0CreatePatient()

        restore_payload = self._doOTARestore()

        case_id_re = re.compile('<case_id>(?P<case_id>\w+)<\/case_id>')
        case_id_xml = case_id_re.search(restore_payload.content).group('case_id')

        casedoc = CommCareCase.get(patient_doc.case_id)
        self.assertEqual(case_id_xml, casedoc._id)

    def test3PushPhoneUpdateXForm(self):
        """
        Check to see if transactional single updates can do it vs. doing all each time
        """
        patient_doc = self.test0CreatePatient()
        allphones = []
        addresses = []
        for n in range(0, self.NUM_PHONES):
            newphone = make_random_cphone()
            newphone['description'] += "%s" % str(n + 1)
            allphones.append(newphone)

            to_send = [None for q in range(0, n)]
            to_send.append(newphone)

            xform = caseapi.phone_addr_updater(patient_doc, to_send, addresses)

            #verify submission worked
            try:
                XFormInstance.get(xform._id)
            except:
                self.fail("XForm submit failed")

            #verify casexml updated
            casedoc_updated = CommCareCase.get(patient_doc.case_id)

            for i, p in enumerate(allphones, start=1):
                self.assertTrue(hasattr(casedoc_updated, 'Phone%d' % i))
                self.assertEquals(p.number, getattr(casedoc_updated, 'Phone%d' % i))
                self.assertEquals(p.description, getattr(casedoc_updated, 'Phone%dType' % i))
                self.assertTrue(hasattr(casedoc_updated, 'Phone%dType' % i))


    def test2PushPhoneWeb(self):
        """
        Verify on the webform that the display is showing up on the patient view.
        """
        patient, phones, addresses = self.test1PatientPhoneAddressCaseXML()
        response = self.client.post('/accounts/login/', {'username': 'mockmock@mockmock.com', 'password': 'mockmock'})

        response = self.client.get(reverse('view_pactpatient', kwargs={'patient_guid': patient._id, 'view_mode': ''}))
        content = response.content

        phone_indices = []
        for p in phones:
            #make sure the numbers are in the right order
            phone_indices.append(content.index(p.number))
        self.assertEquals(sorted(phone_indices), phone_indices)


    def test1PatientPhoneAddressCaseXML(self):
        """
        Test create phone and addresses, submit via casexml and verify casexml gets updated with latest from patient model.
        This does it via API
        """
        patient_doc = self.test0CreatePatient()
        phones = []
        addresses = []
        for n in range(0, self.NUM_PHONES):
            newphone = make_random_cphone()
            newphone['description'] += "%s" % str(n + 1)
            phones.append(newphone)
        for n in range(0, self.NUM_ADDRESSES):
            newaddress = make_random_caddress()
            newaddress['description'] += "%s" % str(n + 1)
            addresses.append(newaddress)
        patient_doc.save()
        #first verify that the case got nothing
        casedoc_blank = CommCareCase.get(patient_doc.case_id)
        for n in range(1, self.NUM_PHONES + 1):
            self.assertFalse(hasattr(casedoc_blank, 'Phone%d' % n))
            self.assertFalse(hasattr(casedoc_blank, 'Phone%dType' % n))

        for n in range(1, self.NUM_ADDRESSES + 1):
            self.assertFalse(hasattr(casedoc_blank, 'address%d' % n))
            self.assertFalse(hasattr(casedoc_blank, 'address%dtype' % n))


        xform = caseapi.phone_addr_updater(patient_doc, phones, addresses)

        #verify submission worked
        try:
            XFormInstance.get(xform._id)
        except:
            self.fail("XForm submit failed")

        #verify casexml updated

        casedoc_updated = CommCareCase.get(patient_doc.case_id)

        for n in range(1, self.NUM_PHONES + 1):
            p = phones[n - 1]
            self.assertTrue(hasattr(casedoc_updated, 'Phone%d' % n))

            self.assertEquals(p.number, getattr(casedoc_updated, 'Phone%d' % n))
            self.assertEquals(p.description, getattr(casedoc_updated, 'Phone%dType' % n))

            self.assertTrue(hasattr(casedoc_updated, 'Phone%dType' % n))
        for n in range(1, self.NUM_ADDRESSES + 1):
            address = addresses[n - 1]
            self.assertTrue(hasattr(casedoc_updated, 'address%d' % n))
            self.assertTrue(hasattr(casedoc_updated, 'address%dtype' % n))
            self.assertEquals(address.description, getattr(casedoc_updated, 'address%dtype' % n))

        #next verify OTA restore
        client = DigestClient()
        client.set_authorization(self.user.username, 'mockmock', 'Digest')
        restore_payload = client.get('/restore')

        print_pretty_xml(restore_payload.content)
        #fails because patient_doc._case is too aggressively sticky
        for n in range(1, self.NUM_PHONES + 1):
            phone = phones[n - 1]
            phone_re = re.compile('<Phone%d>(?P<phone>.*)<\/Phone%d>' % (n, n))
            phone_str = phone_re.search(restore_payload.content).group('phone')
            self.assertEquals(phone.number, phone_str)

            desc_re = re.compile('<Phone%dType>(?P<desc>.*)<\/Phone%dType>' % (n, n))
            desc_str = desc_re.search(restore_payload.content).group('desc')
            self.assertEquals(phone.description, desc_str)



        for n in range(1, self.NUM_ADDRESSES + 1):
            address = addresses[n - 1]
            address_re = re.compile('<address%d>(?P<address>.*)<\/address%d>' % (n, n))
            address_str = address_re.search(restore_payload.content).group('address')
            self.assertEquals(address.get_full_address(), address_str)

            desc_re = re.compile('<address%dtype>(?P<desc>.*)<\/address%dtype>' % (n, n))
            desc_str = desc_re.search(restore_payload.content).group('desc')
            self.assertEquals(address.description, desc_str)


        casedoc = CommCareCase.get(patient_doc.case_id)
        return patient_doc, phones, addresses

    def test0CreatePatient(self):
        """
        Test creates new patients and verify casexml is made alongside them
        Returns a patient couchdoc.
        """
        chws = []
        for x in range(0,5):
            chws.append(self._new_chw(self.tenant, generator.get_or_create_user()))

        pact_id = generator.random_number(length=9)
        response = self.client.post('/accounts/login/', {'username': 'mockmock@mockmock.com', 'password': 'mockmock'})
        response = self.client.post('/patient/new', {
                                                    u'first_name': generator.random_word(),
                                                    u'last_name': generator.random_word(),
                                                    u'middle_name': generator.random_word(),
                                                     'gender':'m',
                                                     'birthdate': '1/1/2000',
                                                     u'pact_id': pact_id,
                                                     'hp_status': random.choice(['HP1','HP2','HP3',]),
                                                     'dot_status': random.choice([ 'DOT3','DOT5','DOT7','DOT1']),
                                                     'art_regimen': 'morning',
                                                     'non_art_regimen': 'morning,evening',
                                                     'primary_hp':  random.choice(chws).django_actor.user.username,
                                                     'patient_id': uuid.uuid4().hex,
                                                     u'notes': generator.random_text(length=160),
                                                     'race': 'asian',
                                                     'is_latino': 'yes',
                                                     'mass_health_expiration': '1/1/2020',
                                                     u'hiv_care_clinic': random.choice(PACT_HIV_CLINIC_CHOICES)[0],
                                                     u'ssn': generator.random_word(length=9),
                                                     'preferred_language': 'english',
                                                     })
        #regimens = 2,1


        fout = open ('foobar.html','w')
        fout.write(response.content)
        fout.close()

        self.assertEquals(response.status_code, 302) #if it's successful, then it'll do a redirect.

        self.assertEqual(1, Patient.objects.all().count())
        patient = Patient.objects.all()[0]

        casedoc = CommCareCase.get(patient.couchdoc.case_id)
        self.assertEquals(casedoc.external_id, patient.couchdoc.pact_id)

        restore_payload = self._doOTARestore()
        #print print_pretty_xml(restore_payload.content)
        return patient.couchdoc



        #start pushing xml submissions via form
        #verify that they get updated on casexml
        #verify on website that those phone numbers appear with client view..




        #setup phone numbers using old style

    def testPatientRegimenChange(self):
        """
        For a given patient created, ensure that it shows up in the OTA restore.
        Ensure also that changes in phone and addresses also show up in OTA restore.
        This test also uses django_digest to authenticate to the OTA restore URL.

        Verify all the phone and address information
        """
        patient_doc = self.test0CreatePatient()

        restore_payload = self._doOTARestore()
        #print print_pretty_xml(restore_payload.content)

        form = PactPatientForm('regimen', instance=patient_doc, data={
                                                                      'art_regimen':'morning,noon,evening',
                                                                      'non_art_regimen':'evening',
                                                                      'first_name': patient_doc.first_name,
                                                                      'last_name': patient_doc.last_name,
                                                                      'preferred_language': patient_doc.preferred_language,
                                                                      'gender': patient_doc.gender,
                                                                      'birthdate': '1/1/2000',
                                                                      'race':patient_doc.race,
                                                                      'hiv_care_clinic':patient_doc.hiv_care_clinic,
                                                                      'primary_hp': patient_doc.primary_hp,
                                                                      'hp_status': patient_doc.hp_status,
                                                                      'dot_status': patient_doc.dot_status
                                                                      })
        #regimens: 1,3

        response = self.client.post('/accounts/login/', {'username': 'mockmock@mockmock.com', 'password': 'mockmock'})
        response = self.client.post(reverse('ajax_post_patient_form', kwargs={'patient_guid':patient_doc._id, 'form_name':'ptedit'}), form.data )

        print "########## posting changed regimen 1"

        restore_payload2 = self._doOTARestore()
        print print_pretty_xml(restore_payload2.content)

        #case_id_re = re.compile('<case_id>(?P<case_id>\w+)<\/case_id>')
        #case_id_xml = case_id_re.search(restore_payload.content).group('case_id')
        form = PactPatientForm('regimen', instance=patient_doc, data={
                                                                      'non_art_regimen':'morning,noon,evening,bedtime',
                                                                      'art_regimen':'morning,evening',
                                                                      'first_name': patient_doc.first_name,
                                                                      'last_name': patient_doc.last_name,
                                                                      'preferred_language': patient_doc.preferred_language,
                                                                      'gender': patient_doc.gender,
                                                                      'birthdate': '1/1/2000',
                                                                      'race':patient_doc.race,
                                                                      'hiv_care_clinic':patient_doc.hiv_care_clinic,
                                                                      'primary_hp': patient_doc.primary_hp,
                                                                      'hp_status': patient_doc.hp_status,
                                                                      'dot_status': patient_doc.dot_status
                                                                      })
        #regimens: 4,2

        response = self.client.post('/accounts/login/', {'username': 'mockmock@mockmock.com', 'password': 'mockmock'})
        response = self.client.post(reverse('ajax_post_patient_form', kwargs={'patient_guid':patient_doc._id, 'form_name':'ptedit'}), form.data )

        print "########## posting changed regimen 2"

        restore_payload3 = self._doOTARestore()
        print print_pretty_xml(restore_payload3.content)


        casedoc = CommCareCase.get(patient_doc.case_id)
        #self.assertEqual(case_id_xml, casedoc._id)
        pass


