from django.test import TestCase
from django.contrib.webdesign import lorem_ipsum
import random
from datetime import timedelta, datetime
from pactpatient.models import PactPatient
from patient.models import Patient, DuplicateIdentifierException
import settings

class basicPatientTest(TestCase):
    def setUp(self):
        Patient.objects.all().delete()


    def testCreatePatient(self):
        oldptcount = Patient.objects.all().count()
        oldcptcount = PactPatient.view('patient/all').count()
        
        newpatient = PactPatient()
        newpatient.first_name = 'mock'
        newpatient.last_name = lorem_ipsum.words(1)
        newpatient.birthdate = (datetime.utcnow() - timedelta(days=random.randint(0,7000))).date()
        newpatient.pact_id = 'mock_id-' + str(random.randint(0,100000))
        newpatient.primary_hp = 'mock-hp-' + str(random.randint(0,100000))
        newpatient.gender = 'f'
        newpatient.save()

        newptcount = Patient.objects.all().count()
        newcptcount = PactPatient.view('patient/all').count()

        self.assertEquals(oldptcount+1, newptcount)
        self.assertEquals(oldcptcount+1, newcptcount)
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







