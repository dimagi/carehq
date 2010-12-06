from django.test import TestCase
import hashlib
import uuid
from patient.models.djangomodels import Patient, DuplicateIdentifierException, DuplicateIdentifierException
from django.contrib.webdesign import lorem_ipsum
import random
from datetime import timedelta, datetime
from patient.models.couchmodels import CPatient

class BasicPatientTests(TestCase):
    def setUp(self):
        Patient.objects.all().delete()


    def testCreatePatient(self):
        oldptcount = Patient.objects.all().count()
        oldcptcount = CPatient.view('patient/all').count()
        
        newpatient = Patient()
        newpatient.cset_first_name('mock')
        newpatient.cset_last_name(lorem_ipsum.words(1))
        newpatient.cset_birthdate((datetime.utcnow() - timedelta(days=random.randint(0,7000))).date())
        newpatient.cset_pact_id('mock_id-' + str(random.randint(0,100000)))
        newpatient.cset_primary_hp('mock-hp-' + str(random.randint(0,100000)))
        newpatient.cset_gender('f')
        newpatient.save()

        newptcount = Patient.objects.all().count()
        newcptcount = CPatient.view('patient/all').count()

        self.assertEquals(oldptcount+1, newptcount)
        self.assertEquals(oldcptcount+1, newcptcount)
        return newpatient

    def testDeletePatient(self):
        oldptcount = Patient.objects.all().count()
        oldcptcount = CPatient.view('patient/all').count()
        pt = self.testCreatePatient()

        newptcount = Patient.objects.all().count()
        newcptcount = CPatient.view('patient/all').count()

        #sanity check that it's there
        self.assertEquals(oldptcount+1, newptcount)
        self.assertEquals(oldcptcount+1, newcptcount)

        pt.delete()

        newptcount = Patient.objects.all().count()
        newcptcount = CPatient.view('patient/all').count()

        self.assertEquals(oldptcount, newptcount)
        self.assertEquals(oldcptcount, newcptcount)
        
    def testCreateDuplicatePactID(self):
        pt1 = self.testCreatePatient()

        try:
            newpatient = Patient()
            newpatient.cset_first_name('mock')
            newpatient.cset_last_name(lorem_ipsum.words(1))
            newpatient.cset_birthdate((datetime.utcnow() - timedelta(days=random.randint(0,7000))).date())
            newpatient.cset_pact_id(pt1.couchdoc.pact_id)
            newpatient.cset_primary_hp('mock-hp-' + str(random.randint(0,100000)))
            newpatient.cset_gender('f')
            newpatient.save()
            self.fail("Error, you should not be able to save a patient with duplicate pact ids")
        except DuplicateIdentifierException, e:
            pass #yay, success at finding the bad pactid
        except Exception, e:
            self.fail("Wrong exception expected, expected DuplicateIdentifierException, but got %s" % (e))







