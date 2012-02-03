#import uuid
import pdb
import uuid
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.contrib.webdesign import lorem_ipsum
import random
from datetime import timedelta, datetime
from clinical_shared.tests.testcase import CareHQClinicalTestCase
from clinical_shared.utils import generator
from .pactpatient_test_utils import delete_all
from pactpatient.models import PactPatient
from patient.models import Patient, DuplicateIdentifierException
from permissions.models import Actor, Role, PrincipalRoleRelation
import settings

#'pact_id','first_name', 'middle_name', 'last_name', 'gender', 'birthdate', 'race', 'is_latino',
#                        'preferred_language', 'mass_health_expiration', 'hiv_care_clinic', 'ssn', 'notes',
#                        'primary_hp', 'arm', 'art_regimen', 'non_art_regimen',]
from tenant.models import Tenant

class patientViewTests(CareHQClinicalTestCase):
    def setUp(self):
        User.objects.all().delete()
        Actor.objects.all().delete()
        Role.objects.all().delete()
        Tenant.objects.all().delete()
        PrincipalRoleRelation.objects.all().delete()
        delete_all(PactPatient, 'patient/all')
        call_command('carehq_init')
        self.tenant = Tenant.objects.all()[0]
        self._createUser()
        self.client = Client()


    def testCreatePatientView(self):
        chws = []
        for x in range(0,5):
            chws.append(self._new_chw(self.tenant, generator.get_or_create_user()))

        response = self.client.post('/accounts/login/', {'username': 'mockmock@mockmock.com', 'password': 'mockmock'})

        response = self.client.post('/patient/new', {'first_name':'foo',
                                                      'last_name': 'bar',
                                                      'gender':'m',
                                                      'birthdate': '1/1/2000',
                                                      'pact_id': 'mockmock',
                                                      'arm': 'DOT',
                                                      'art_regimen': 'QD',
                                                      'non_art_regimen': 'BID',
                                                      'primary_hp':  random.choice(chws).django_actor.user.username,
                                                      'patient_id': uuid.uuid4().hex,
                                                      'race': 'asian',
                                                      'is_latino': 'yes',
                                                      'mass_health_expiration': '1/1/2020',
                                                      'hiv_care_clinic': 'brigham_and_womens_hospital',
                                                      'ssn': '1112223333',
                                                      'preferred_language': 'english',

                                                    })

        self.assertEquals(response.status_code, 302) #if it's successful, then it'll do a redirect.
    def testCreatePatientViewFailed(self):
        response = self.client.post('/accounts/login/', {'username': 'mockmock@mockmock.com', 'password': 'mockmock'})

        response = self.client.post('/patient/new', {'first_name':'foo',
                                                      #'last_name': 'bar',
                                                      'gender':'m',
                                                      'birthdate': '1/1/2000',
                                                      'pact_id': 'mockmock',
                                                      'arm': 'DOT',
                                                      'art_regimen': 'QD',
                                                      'non_art_regimen': 'BID',
#                                                     'primary_hp': 'isaac',
                                                      'patient_id': uuid.uuid4().hex,
                                                      'race': 'asian',
                                                      'is_latino': 'yes',
                                                      'mass_health_expiration': '1/1/2020',
                                                      'hiv_care_clinic': 'brigham_and_womens_hospital',
                                                      'ssn': '1112223333',
                                                      'preferred_language': 'english',
                                                    })

        self.assertEquals(response.status_code, 200) #if it's failed, it'll still register a false
        self.assertTrue(response.content.count('class="errorField"') > 0)
        self.assertTrue(response.content.count("This field is required") > 0)

    def testCreatePatientViewDupe(self):
        chws = []
        for x in range(0,5):
            chws.append(self._new_chw(self.tenant, generator.get_or_create_user()))

        response = self.client.post('/accounts/login/', {'username': 'mockmock@mockmock.com', 'password': 'mockmock'})

        pact_id = uuid.uuid4().hex
        #create first one, should worok
        response = self.client.post('/patient/new', {'first_name':'foo',
                                                      'last_name': 'bar',
                                                      'gender':'m',
                                                      'birthdate': '1/1/2000',
                                                      'pact_id': pact_id,
                                                      'arm': 'DOT',
                                                      'art_regimen': 'QD',
                                                      'non_art_regimen': 'BID',
                                                      'primary_hp': random.choice(chws).django_actor.user.username,
                                                      'patient_id': uuid.uuid4().hex,
                                                      'race': 'asian',
                                                      'is_latino': 'yes',
                                                      'mass_health_expiration': '1/1/2020',
                                                      'hiv_care_clinic': 'brigham_and_womens_hospital',
                                                      'ssn': '1112223333',
                                                      'preferred_language': 'english',

                                                    })
        self.assertEquals(response.status_code, 302) #if it's failed, it'll still register a false
        response = self.client.post('/patient/new', {'first_name':'foo',
                                              'last_name': 'bar',
                                              'gender':'m',
                                              'birthdate': '1/1/2000',
                                              'pact_id': pact_id,
                                              'arm': 'DOT',
                                              'art_regimen': 'QD',
                                              'non_art_regimen': 'BID',
                                              'primary_hp': random.choice(chws).django_actor.user.username,
                                              'patient_id': uuid.uuid4().hex,
                                              'race': 'asian',
                                              'is_latino': 'yes',
                                              'mass_health_expiration': '1/1/2020',
                                              'hiv_care_clinic': 'brigham_and_womens_hospital',
                                              'ssn': '1112223333',
                                              'preferred_language': 'english',
                                            })
        self.assertEquals(response.status_code, 200) #failure at 200

        self.assertTrue(response.content.count("Error, pact id must be unique") > 0)

    def testCreateAndChangeHP(self):
        chws = []
        for x in range(0,5):
            chws.append(self._new_chw(self.tenant, generator.get_or_create_user()))

        response = self.client.post('/accounts/login/', {'username': 'mockmock@mockmock.com', 'password': 'mockmock'})

        pact_id = uuid.uuid4().hex



        patient_dict = {'first_name':'foo',
                        'last_name': 'bar',
                        'gender':'m',
                        'birthdate': '1/1/2000',
                        'pact_id': pact_id,
                        'arm': 'DOT',
                        'art_regimen': 'QD',
                        'non_art_regimen': 'BID',
                        'primary_hp': chws[0].django_actor.user.username,
                        'patient_id': uuid.uuid4().hex,
                        'race': 'asian',
                        'is_latino': 'yes',
                        'mass_health_expiration': '1/1/2020',
                        'hiv_care_clinic': 'brigham_and_womens_hospital',
                        'ssn': '1112223333',
                        'preferred_language': 'english',
                        }
        response = self.client.get(reverse('new_pactpatient')) #in a regular world this is what happens, do a get first.
        response = self.client.post(reverse('new_pactpatient'), patient_dict)
        patient_doc = PactPatient.view('pactcarehq/patient_pact_ids', key=pact_id, include_docs=True).first()
        #assert that the first CHW is now given a PRR for that patient.
        self.assertEquals(PrincipalRoleRelation.objects.filter(actor=chws[0].django_actor).filter(content_id=patient_doc.django_uuid).count(), 1)
        self.assertEquals(PrincipalRoleRelation.objects.filter(actor=chws[1].django_actor).filter(content_id=patient_doc.django_uuid).count(), 0)
        self.assertEquals(PrincipalRoleRelation.objects.filter(actor=chws[2].django_actor).filter(content_id=patient_doc.django_uuid).count(), 0)

        #next, repost
        patient_dict['primary_hp']=chws[1].django_actor.user.username
        response=self.client.post(reverse('ajax_post_patient_form', kwargs={'patient_guid': patient_doc._id, 'form_name':'ptedit'}), patient_dict)
        self.assertEquals(PrincipalRoleRelation.objects.filter(actor=chws[0].django_actor).filter(content_id=patient_doc.django_uuid).count(), 0)
        self.assertEquals(PrincipalRoleRelation.objects.filter(actor=chws[1].django_actor).filter(content_id=patient_doc.django_uuid).count(), 1)
        self.assertEquals(PrincipalRoleRelation.objects.filter(actor=chws[2].django_actor).filter(content_id=patient_doc.django_uuid).count(), 0)

class basicPatientTest(CareHQClinicalTestCase):
    """
    Really low level API testing on the interaction of django patient and couch patient.
    """

    def setUp(self):
        User.objects.all().delete()
        Actor.objects.all().delete()
        Role.objects.all().delete()
        Tenant.objects.all().delete()
        PrincipalRoleRelation.objects.all().delete()
        delete_all(PactPatient, 'patient/all')
        Patient.objects.all().delete()
        call_command('carehq_init')
        self.tenant = Tenant.objects.all()[0]
        self._createUser()
        delete_all(PactPatient, 'patient/all')
        self.client = Client()


    def testCreatePatientDjango(self):
        old_django_count = Patient.objects.all().count()
        old_couch_count = PactPatient.view('patient/all').count()
        
        newpatient = PactPatient()
        newpatient.first_name = 'mock'
        newpatient.last_name = lorem_ipsum.words(1)
        newpatient.birthdate = (datetime.utcnow() - timedelta(days=random.randint(0,7000))).date()
        newpatient.pact_id = 'mock_id-' + str(random.randint(0,100000))
        newpatient.primary_hp = 'mock-hp-' + str(random.randint(0,100000))
        newpatient.gender = 'f'
        newpatient.save()

        new_django_count = Patient.objects.all().count()

        new_couch_count = PactPatient.view('patient/all').count()

        self.assertEquals(old_django_count+1, new_django_count)
        self.assertEquals(old_couch_count+1, new_couch_count)
        return newpatient

    def testDeletePatientFromDjango(self):
        start_pt_count= Patient.objects.all().count()
        start_couch_pt_count = PactPatient.view('patient/all').count()
        pt_document = self.testCreatePatientDjango()
        django_pt = Patient.objects.get(id=pt_document.django_uuid)

        create_pt_count = Patient.objects.all().count()
        create_couch_pt_count = PactPatient.view('patient/all').count()

        #sanity check that it's there
        self.assertEquals(start_pt_count+1, create_pt_count)
        self.assertEquals(start_couch_pt_count+1, create_couch_pt_count)

        django_pt.delete()

        del_pt_count = Patient.objects.all().count()
        del_couch_pt_count = PactPatient.view('patient/all').count()

        self.assertEquals(start_pt_count, del_pt_count)
        self.assertEquals(start_couch_pt_count, del_couch_pt_count)


    def testDeletePatientFromCouchDoc(self):
        start_pt_count= Patient.objects.all().count()
        start_couch_pt_count = PactPatient.view('patient/all').count()
        pt_document = self.testCreatePatientDjango()

        create_pt_count = Patient.objects.all().count()
        create_couch_pt_count = PactPatient.view('patient/all').count()

        #sanity check that it's there
        self.assertEquals(start_pt_count+1, create_pt_count)
        self.assertEquals(start_couch_pt_count+1, create_couch_pt_count)

        pt_document.delete()

        del_pt_count = Patient.objects.all().count()
        del_couch_pt_count = PactPatient.view('patient/all').count()

        self.assertEquals(start_pt_count, del_pt_count)
        self.assertEquals(start_couch_pt_count, del_couch_pt_count)

    def testCreateDuplicatePatient(self):
        pt1 = self.testCreatePatientDjango()

        try:
            newpatient = PactPatient()
            newpatient.first_name = 'mock'
            newpatient.last_name = lorem_ipsum.words(1)
            newpatient.birthdate = (datetime.utcnow() - timedelta(days=random.randint(0,7000))).date()
            newpatient.pact_id = pt1.pact_id
            newpatient.primary_hp = 'mock-hp-' + str(random.randint(0,100000))
            newpatient.gender = 'f'
            newpatient.save()
            self.fail("error, you should not be able to save a patient with duplicate pact ids")
        except DuplicateIdentifierException, e:
            pass #yay, success at finding the bad pactid
        except Exception, e:
            self.fail("wrong exception expected, expected DuplicateIdentifierException, but got %s" % (e))







