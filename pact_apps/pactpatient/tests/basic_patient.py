#import uuid
import uuid
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.contrib.webdesign import lorem_ipsum
import random
from datetime import timedelta, datetime
from .pactpatient_test_utils import delete_all
from pactpatient.models import PactPatient
from patient.models import Patient, DuplicateIdentifierException
import settings

#'pact_id','first_name', 'middle_name', 'last_name', 'gender', 'birthdate', 'race', 'is_latino',
#                        'preferred_language', 'mass_health_expiration', 'hiv_care_clinic', 'ssn', 'notes',
#                        'primary_hp', 'arm', 'art_regimen', 'non_art_regimen',]

class patientViewTests(TestCase):
    def setUp(self):
        User.objects.all().delete()
        Patient.objects.all().delete()
        delete_all(PactPatient, 'patient/all')
        self.client = Client()
        self._createUser()

    def _createUser(self):
        usr = User()
        usr.username = 'mockmock@mockmock.com'
        usr.set_password('mockmock')
        usr.first_name='mocky'
        usr.last_name = 'mock'
        usr.save()
    def testCreatePatientView(self):
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

                                                    })

        self.assertEquals(response.status_code, 302) #if it's successful, then it'll do a redirect.
    def testCreatePatientViewFailed(self):
        response = self.client.post('/accounts/login/', {'username': 'mockmock@mockmock.com', 'password': 'mockmock'})

        response = self.client.post('/patient/new', {'first_name':'foo',
                                                      'last_name': 'bar',
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
                                                      'primary_hp': 'isaac',
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
                                              'primary_hp': 'isaac',
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

class basicPatientTest(TestCase):
    def _createUser(self):
        usr = User()
        usr.username = 'mockmock@mockmock.com'
        usr.set_password('mockmock')
        usr.first_name='mocky'
        usr.last_name = 'mock'
        usr.save()

    def setUp(self):
        User.objects.all().delete()
        Patient.objects.all().delete()
        delete_all(PactPatient, 'patient/all')
        self.client = Client()
        self._createUser()


    def testCreatePatient(self):
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
        pt_document = self.testCreatePatient()
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
        pt_document = self.testCreatePatient()

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
    def testModifyPatient(self):
        pt = self.testCreatePatient()
        pt.last_name = "fooo change"
        pt.save()

        pt.first_name = "fooooo changed again"
        pt.save()
        
    def testCreateDuplicatePatient(self):
        pt1 = self.testCreatePatient()

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







