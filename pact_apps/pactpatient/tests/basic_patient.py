from django.test import TestCase
from django.contrib.webdesign import lorem_ipsum
import random
from datetime import timedelta, datetime
from pactpatient.models.pactmodels import PactPatient
from patient.models import Patient, DuplicateIdentifierException

class basicPatientTest(TestCase):
    def setUp(self):
        Patient.objects.all().delete()


    def testCreatePatient(self):
        oldptcount = Patient.objects.all().count()
        oldcptcount = PactPatient.view('patient/all').count()
        
        newpatient = Patient()
        newpatient.couchdoc.first_name = 'mock'
        newpatient.couchdoc.last_name = lorem_ipsum.words(1)
        newpatient.couchdoc.birthdate = (datetime.utcnow() - timedelta(days=random.randint(0,7000))).date()
        newpatient.couchdoc.pact_id = 'mock_id-' + str(random.randint(0,100000))
        newpatient.couchdoc.primary_hp = 'mock-hp-' + str(random.randint(0,100000))
        newpatient.couchdoc.gender = 'f'
        newpatient.save()

        newptcount = Patient.objects.all().count()
        newcptcount = PactPatient.view('patient/all').count()

        self.assertequals(oldptcount+1, newptcount)
        self.assertequals(oldcptcount+1, newcptcount)
        return newpatient

    def testDeletePatient(self):
        oldptcount = Patient.objects.all().count()
        oldcptcount = PactPatient.view('patient/all').count()
        pt = self.testCreatePatient()

        newptcount = Patient.objects.all().count()
        newcptcount = PactPatient.view('patient/all').count()

        #sanity check that it's there
        self.assertequals(oldptcount+1, newptcount)
        self.assertequals(oldcptcount+1, newcptcount)

        pt.delete()

        newptcount = Patient.objects.all().count()
        newcptcount = PactPatient.view('patient/all').count()

        self.assertequals(oldptcount, newptcount)
        self.assertequals(oldcptcount, newcptcount)
    def testModifyPatient(self):
        pt = self.testCreatePatient()
        pt.couchdoc.last_name = "fooo change"
        pt.couchdoc.save()

        pt.couchdoc.first_name = "fooooo changed again"
        pt.save()
        
    def testCreateDuplicatePatient(self):
        pt1 = self.testCreatePatient()

        try:
            newpatient = Patient()
            newpatient.couchdoc.first_name = 'mock'
            newpatient.couchdoc.last_name = lorem_ipsum.words(1)
            newpatient.couchdoc.birthdate = (datetime.utcnow() - timedelta(days=random.randint(0,7000))).date()
            newpatient.couchdoc.pact_id = pt1.couchdoc.pact_id
            newpatient.couchdoc.primary_hp = 'mock-hp-' + str(random.randint(0,100000))
            newpatient.couchdoc.gender = 'f'
            newpatient.save()
            self.fail("error, you should not be able to save a patient with duplicate pact ids")
        except DuplicateIdentifierException, e:
            pass #yay, success at finding the bad pactid
        except exception, e:
            self.fail("wrong exception expected, expected DuplicateIdentifierException, but got %s" % (e))







