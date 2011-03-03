from django.test import TestCase
import hashlib
import uuid
from django.contrib.auth.models import User
from casetracker.models import Case
from clinical_core.clincore.utils import generator

INITIAL_DESCRIPTION = "this is a case made by the test case"
CHANGED_DESCRIPTION = 'i just changed it, foo'

###helper functions
def create_user(username='mockuser', password='mockmock'):    
    user = User()    
    user.username = username
    # here, we mimic what the django auth system does
    # only we specify the salt to be 12345
    salt = '12345'
    hashed_pass = hashlib.sha1(salt+password).hexdigest()
    user.password = 'sha1$%s$%s' % (salt, hashed_pass)
    
    user.set_password(password)
    user.save()
    return user


class BasicCaseTests(TestCase):
    #fixtures = ['samplesetup-fixture.json']

    def setUp(self):
        pass

#    @transaction.commit_manually
#    def tearDown(self):
#        Case.objects.all().delete()
#        Actor.objects.all().delete()
#        Role.objects.all().delete()
#        PatientActorLink.objects.all().delete()
#        Patient.objects.all().delete()
#        Category.objects.all().delete()
#        User.objects.all().delete()
#        transaction.commit()

    def testCreateCaseApi(self, description=INITIAL_DESCRIPTION):
        """Simple test:  Create a case and verify that it exists in the database via the API"""
        #get the basic counts

        user1 = generator.get_or_create_user()
        user2 = generator.get_or_create_user()

        caregiver_creator = generator.generate_actor(user1, 'caregiver')
        provider_assigned = generator.generate_actor(user2, 'provider')

        old_case_count = Case.view('casetracker/cases_by_id').count()
        old_event_count = Case.view('casetracker/all_case_events_date').count()
        newcase = Case.create(caregiver_creator, description, "mock body %s" % (uuid.uuid1().hex), assigned_to=provider_assigned)

        #is the thing created?
        new_case_count = Case.view('casetracker/cases_by_id').count()
        new_event_count = Case.view('casetracker/all_case_events_date').count()
        self.assertEqual(new_case_count, old_case_count + 1)
        self.assertEqual(new_event_count, old_event_count + 1)

        events = newcase.events
        self.assertEqual(1,len(events))
        #verify that said case count is a new case event of type "open"
        self.assertEqual('open', events[0].activity.slug)
        return newcase

    def testModifyCase(self):
        case = self.testCreateCaseApi()
        old_event_count = Case.view('casetracker/all_case_events_date').count()
        case.description = "changing description " + uuid.uuid1().hex
        case.save()


        new_event_count = Case.view('casetracker/all_case_events_date').count()
        self.assertEqual(new_event_count, old_event_count + 1)


        events = case.events
        self.assertEqual('edit', events[-1].activity.slug)
        self.assertEqual(2, len(events))

    
    def testCaseModifyClient(self, description = "A test case that modifies a case via the webUI using the web client."):
        #self.assertFalse(True)
        pass


    def testCaseModifyDescriptionApi(self):
        desc= uuid.uuid1().hex
        case = self.testCreateCaseApi(description=desc)

        user1 = generator.get_or_create_user()
        actor1 = generator.generate_actor(user1, 'provider')

        
        dbcase = Case.view('casetracker/cases_by_id', key=case._id)
        case.description = CHANGED_DESCRIPTION 
        case.last_edit_by = actor1.id
        #activity = ActivityClass.objects.filter(event_class=constants.CASE_EVENT_EDIT)[0]
        case.save_comment="editing in testCaseModifyDescription"
        case.save()#activity=activity)
        
        
        #events = CaseEvent.objects.filter(case=case)
        #we just did an edit, so it should be 2        
        #self.assertEqual(2, events.count())
        
        #the top one due to the sort ordering should be the one we just did
        #self.assertEqual(constants.CASE_EVENT_EDIT, events[0].activity.event_class)
        
        #quickly verify that the original description is still unchanged
        dbcase = Case.view('casetracker/cases_by_id', key=case._id).first()
        self.assertEqual(dbcase._id, case._id)        


    def testCaseCreateChildCases(self):
        oldcase = self.testCreateCaseApi()
        user1 = generator.get_or_create_user()
        actor1 = generator.generate_actor(user1, 'provider')
        CHILD_CASES=10
        for num in range(0,CHILD_CASES):
            desc = uuid.uuid1().hex
            newcase = self.testCreateCaseApi(description=desc)
            newcase.parent_case = oldcase._id
            newcase.last_edit_by = actor1.id
            newcase.save_comment="editing in testCaseCreateChildCases"
            newcase.save()#activity=activity)

        self.assertEqual(len(oldcase.child_cases), CHILD_CASES)
        
        
        
        
        
        
        