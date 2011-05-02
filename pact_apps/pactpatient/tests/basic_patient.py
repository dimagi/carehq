from django.test import testcase
from pactpatient.models.pactmodels import cpatient
from patient.models.djangomodels import patient, duplicateidentifierexception, duplicateidentifierexception
from django.contrib.webdesign import lorem_ipsum
import random
from datetime import timedelta, datetime

class basicpatienttests(testcase):
    def setup(self):
        patient.objects.all().delete()


    def testcreatepatient(self):
        oldptcount = patient.objects.all().count()
        oldcptcount = cpatient.view('patient/all').count()
        
        newpatient = patient()
        newpatient.cset_first_name('mock')
        newpatient.cset_last_name(lorem_ipsum.words(1))
        newpatient.cset_birthdate((datetime.utcnow() - timedelta(days=random.randint(0,7000))).date())
        newpatient.cset_pact_id('mock_id-' + str(random.randint(0,100000)))
        newpatient.cset_primary_hp('mock-hp-' + str(random.randint(0,100000)))
        newpatient.cset_gender('f')
        newpatient.save()

        newptcount = patient.objects.all().count()
        newcptcount = cpatient.view('patient/all').count()

        self.assertequals(oldptcount+1, newptcount)
        self.assertequals(oldcptcount+1, newcptcount)
        return newpatient

    def testdeletepatient(self):
        oldptcount = patient.objects.all().count()
        oldcptcount = cpatient.view('patient/all').count()
        pt = self.testcreatepatient()

        newptcount = patient.objects.all().count()
        newcptcount = cpatient.view('patient/all').count()

        #sanity check that it's there
        self.assertequals(oldptcount+1, newptcount)
        self.assertequals(oldcptcount+1, newcptcount)

        pt.delete()

        newptcount = patient.objects.all().count()
        newcptcount = cpatient.view('patient/all').count()

        self.assertequals(oldptcount, newptcount)
        self.assertequals(oldcptcount, newcptcount)
        
    def testcreateduplicatepactid(self):
        pt1 = self.testcreatepatient()

        try:
            newpatient = patient()
            newpatient.cset_first_name('mock')
            newpatient.cset_last_name(lorem_ipsum.words(1))
            newpatient.cset_birthdate((datetime.utcnow() - timedelta(days=random.randint(0,7000))).date())
            newpatient.cset_pact_id(pt1.couchdoc.pact_id)
            newpatient.cset_primary_hp('mock-hp-' + str(random.randint(0,100000)))
            newpatient.cset_gender('f')
            newpatient.save()
            self.fail("error, you should not be able to save a patient with duplicate pact ids")
        except duplicateidentifierexception, e:
            pass #yay, success at finding the bad pactid
        except exception, e:
            self.fail("wrong exception expected, expected duplicateidentifierexception, but got %s" % (e))







