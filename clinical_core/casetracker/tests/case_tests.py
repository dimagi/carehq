
from django.test import TestCase
from datetime import datetime
import hashlib
import uuid
from django.contrib.auth.models import User
from casetracker.models import Case, Status, ActivityClass, CaseEvent, Priority, Category
from clinical_core.clincore import test_bootstrap as bootstrap
from casetracker import constants
from patient.models.djangomodels import Patient
from actors.models.actors import PatientActorLink, Actor
from actors.models.roles import Role, Role
from django.core.management import call_command
from django.db import transaction


INITIAL_DESCRIPTION = "this is a case made by the test case"
CHANGED_DESCRIPTION = 'i just changed it, foo'


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


class EventActivityVerificationTest(TestCase):
    fixtures = [
                'blah.json']

    def setUp(self):
        call_command('load_categories')

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


    def testCreateCaseView(self, description = INITIAL_DESCRIPTION):
        #self.assertFalse(True)
        pass


    def testCreateCaseApi(self, description=INITIAL_DESCRIPTION):
        ###########################
        #get the basic counts
        user1 = bootstrap.generate_user()
        user2 = bootstrap.generate_user()

        actor1 = bootstrap.generate_actor(user1, 'caregiver')
        actor2 = bootstrap.generate_actor(user2, 'provider')

        oldcasecount = Case.objects.all().count()
        oldevents = CaseEvent.objects.all().count()

#        newcase = Case()
#        newcase.description = description
#        newcase.opened_by = actor1
#        newcase.last_edit_by = actor1
#
#        newcase.assigned_date = datetime.utcnow()
#        newcase.assigned_to = actor2
#        newcase.category = Category.objects.all()[0]
#        newcase.status = Status.objects.all().filter(state_class=constants.CASE_STATE_OPEN)[0]
#        newcase.priority = Priority.objects.all()[0]
#        activity = ActivityClass.objects.filter(event_class=constants.CASE_EVENT_OPEN)[0]
#        newcase.save(activity=activity)

        newcase = Case.objects.new_case(Category.objects.all()[0],
                              actor1,
                              description,
                              "mock body %s" % (uuid.uuid1().hex),
                              Priority.objects.all()[0],
                              status=Status.objects.all().filter(state_class=constants.CASE_STATE_OPEN)[0],
                              activity=ActivityClass.objects.filter(event_class=constants.CASE_EVENT_OPEN)[0]
                              )

        #is the thing created?
        self.assertEqual(Case.objects.all().count(), oldcasecount + 1)
        self.assertEqual(CaseEvent.objects.all().count(), oldevents + 1)
        #verify that the case count created has created a new caseevent
        events = CaseEvent.objects.filter(case=newcase)
        self.assertEqual(1,events.count())
        #verify that said case count is a new case event of type "open"
        self.assertEqual(constants.CASE_EVENT_OPEN, events[0].activity.event_class)
        return newcase
    
    def testCaseModifyClient(self, description = "A test case that modifies a case via the webUI using the web client."):
        #self.assertFalse(True)
        pass


    def testCaseModifyDescriptionApi(self):
        desc= uuid.uuid1().hex
        self.testCreateCaseApi(description=desc)

        user1 = bootstrap.generate_user()
        actor1 = bootstrap.generate_actor(user1, 'provider')

        
        case = Case.objects.all().get(description=desc)
        case.description = CHANGED_DESCRIPTION
        case.last_edit_by = actor1
        activity = ActivityClass.objects.filter(event_class=constants.CASE_EVENT_EDIT)[0]
        case.save_comment="editing in testCaseModifyDescription"
        case.save(activity=activity)
        
        
        events = CaseEvent.objects.filter(case=case)
        #we just did an edit, so it should be 2        
        self.assertEqual(2, events.count())
        
        #the top one due to the sort ordering should be the one we just did
        self.assertEqual(constants.CASE_EVENT_EDIT, events[0].activity.event_class)
        
        
        #quickly verify that the original description is still unchanged
        dbcase = Case.objects.all().get(description=CHANGED_DESCRIPTION)
        self.assertEqual(dbcase.id, case.id)        
        self.assertEqual(dbcase.orig_description, desc)
    

    def testCaseCreateChildCases(self):
        self.testCreateCaseApi()
        user1 = bootstrap.generate_user()
        actor1 = bootstrap.generate_actor(user1, 'provider')

        case = Case.objects.all().get(description =INITIAL_DESCRIPTION)
        CHILD_CASES=10
        for num in range(0,CHILD_CASES):
            desc = uuid.uuid1().hex
            newcase = self.testCreateCaseApi(description=desc)
            newcase.parent_case = case
            newcase.last_edit_by = actor1
            activity = ActivityClass.objects.filter(event_class=constants.CASE_EVENT_EDIT)[0]
            newcase.save_comment="editing in testCaseCreateChildCases"
            newcase.save(activity=activity)
            
            
        self.assertEqual(case.child_cases.count(), CHILD_CASES)
        
        
        
        
        
        
        