from django.test import TestCase
from datetime import datetime
import hashlib
import uuid
from django.contrib.auth.models import User
from casetracker.models import Case, Status, EventActivity, CaseEvent, Priority, Category
from casetracker import constants


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
    fixtures = ['0-caseaction.json',
                '3-priority.json',
                ]

    def setUp(self):
        from ashandapp.caseregistry import issue
        from ashandapp.caseregistry import question
        issue.register_category()        
        question.register_category()         
        create_user()
        Case.objects.all().delete()

    def testCreateCase(self, description="this is a case made by the test case"):
        
        oldcasecount = Case.objects.all().count()
        oldevents = CaseEvent.objects.all().count()
        
        
        user = User.objects.get(username='mockuser')
        newcase = Case()
        newcase.description = description
        newcase.opened_by = user
        newcase.assigned_date = datetime.utcnow()
        newcase.assigned_to = user
        
        newcase.category = Category.objects.all()[0]
        newcase.status = Status.objects.all().filter(category=newcase.category).filter(state_class=constants.CASE_STATE_OPEN)[0]
        newcase.priority = Priority.objects.all()[0]
        
        newcase.save()
        
        #is the thing created?
        self.assertEqual(Case.objects.all().count(), oldcasecount + 1)
        self.assertEqual(CaseEvent.objects.all().count(), oldevents + 1)
        
        #verify that the case count created has created a new caseevent
        events = CaseEvent.objects.filter(case=newcase)
        self.assertEqual(1,events.count())
        #verify that said case count is a new case event of type "open"
        self.assertEqual(constants.CASE_EVENT_OPEN, events[0].activity.event_class)
        return newcase
    
    def testCaseModifyDescription(self):
        desc= uuid.uuid1().hex
        self.testCreateCase(description=desc)
        user = User.objects.get(username='mockuser')
        
        case = Case.objects.all().get(description = desc)
        case.description = "i just changed it, foo"
        case.last_edit_by = user
        activity = EventActivity.objects.filter(category=case.category).filter(event_class=constants.CASE_EVENT_EDIT)[0]
        case.save(activity=activity, save_comment="editing in testCaseModifyDescription")
        
        
        events = CaseEvent.objects.filter(case=case)
        #we just did an edit, so it should be 2        
        self.assertEqual(2, events.count())
        
        #the top one due to the sort ordering should be the one we just did
        self.assertEqual(constants.CASE_EVENT_EDIT, events[1].activity.event_class)
        
        
        #quickly verify that the original description is still unchanged
        dbcase = Case.objects.all().get(description='i just changed it, foo')
        self.assertEqual(dbcase.id, case.id)        
        self.assertEqual(dbcase.orig_description, desc)
    
    def _makeCase(self, user):        
        newcase = Case()
        newcase.description = uuid.uuid1().hex
        newcase.opened_by = user
        newcase.assigned_date = datetime.utcnow()
        newcase.assigned_to = user
        
        newcase.category = Category.objects.all()[0]
        newcase.status = Status.objects.all()[0]
        newcase.priority = Priority.objects.all()[0]
        
        newcase.save()
        return newcase
    
    def testCaseCreateChildCases(self):
        self.testCreateCase()
        user = User.objects.get(username='mockuser')
        case = Case.objects.all().get(description = "this is a case made by the test case")
        CHILD_CASES=10
        for num in range(0,CHILD_CASES):
            desc = uuid.uuid1().hex
            newcase = self.testCreateCase(description=desc)
            newcase.parent_case = case
            newcase.last_edit_by = user
            activity = EventActivity.objects.filter(category=case.category).filter(event_class=constants.CASE_EVENT_EDIT)[0]
            newcase.save(activity=activity, save_comment="editing in testCaseCreateChildCases")
            
            
        self.assertEqual(case.child_cases.count(), CHILD_CASES)
        
        
        
        
        
        
        