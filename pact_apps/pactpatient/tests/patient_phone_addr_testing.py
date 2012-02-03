from unittest.case import TestCase
import simplejson
from django.contrib.auth.models import User
import os
from casexml.apps.case.models import CommCareCase
from pactpatient.scripts.migrate4_cleanup_case_phone_addrs import do_reset_phone_addrs, cleanup_addrs, cleanup_phones
import settings

class patientCaseUpdateTests(TestCase):
    START_CASE = 0
    END_CASE=1
    def _createUser(self):
        User.objects.all().delete()
        usr = User()
        usr.username = 'admin'
        usr.set_password('mockmock')
        usr.first_name='mocky'
        usr.last_name = 'mock'
        usr.save()
    def setUp(self):
        self.db = CommCareCase.get_db()
        fin = open(os.path.join(settings.filepath, 'cases.json'))
        self.cases = simplejson.loads(fin.read())
        self._createUser()
#    def testVerifyCount(self):
#        self.assertEqual(122, len(self.cases))

    def testLoadIntoDB(self):

        test_cases = self.cases

        case_ids = [x['_id'] for x in test_cases]
        self.db.save_docs(test_cases)

        db_cases = [CommCareCase.get(x) for x in case_ids]
        self.assertEqual(len(test_cases), len(db_cases))

        for case in test_cases:
            #these are the originals
            db_case= CommCareCase.get(case['_id'])
            addrs_cleaned = cleanup_addrs(db_case)
            phones_cleaned = cleanup_phones(db_case)
            do_reset_phone_addrs(db_case)
            db_case2 = CommCareCase.get(case['_id'])

            self.assertEqual(len(addrs_cleaned), len(cleanup_addrs(db_case2)))
            self.assertEqual(len(phones_cleaned), len(cleanup_phones(db_case2)))




        


