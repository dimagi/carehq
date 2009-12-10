from django.test import TestCase
from datetime import datetime
import hashlib
from django.contrib.auth.models import User
from casetracker.models import Case, Status, EventActivity, CaseEvent, Priority, Category

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
                '1-category.json',
                '2-eventactivity.json',
                '3-priority.json',
                '4-status.json',
                ]

    def setUp(self):
        create_user()

    def testCreateCase(self):
        
        oldcasecount = Case.objects.all().count()
        oldevents = CaseEvent.objects.all().count()
        
        user = User.objects.get(username='mockuser')
        newcase = Case()
        newcase.description = "this is a case made by the test case"
        newcase.opened_by = user
        
        newcase.category = Category.objects.all()[0]
        newcase.status = Status.objects.all()[0]
        newcase.priority = Priority.objects.all()[0]
        
        newcase.save()
        
        #is the thing created?
        self.assertEqual(Case.objects.all().count(), oldcasecount + 1)
        self.assertEqual(CaseEvent.objects.all().count(), oldevents + 1)
        
        #verify that the case count created has created a new caseevent
        events = CaseEvent.objects.filter(case=newcase)        
        self.assertEqual(1,events.count())
        #verify that said case count is a new case event of type "open"
        self.assertEqual("open", events[0].activity.event_class)
    
    def testCaseModifyDescription(self):
        self.testCreateCase()
        user = User.objects.get(username='mockuser')
        
        case = Case.objects.all().get(description = "this is a case made by the test case")
        case.description = "i just changed it, foo"
        case.last_edit_by = user
        case.save()
        
        
        events = CaseEvent.objects.filter(case=case)
        #we just did an edit, so it should be 2        
        self.assertEqual(2, events.count())
        
        #the top one due to the sort ordering should be the one we just did
        self.assertEqual("edit", events[1].activity.event_class)
        
        
        #quickly verify that the original description is still unchanged
        dbcase = Case.objects.all().get(description='i just changed it, foo')
        self.assertEqual(dbcase.id, case.id)        
        self.assertEqual(dbcase.orig_description, "this is a case made by the test case")
        
        
        
        
        
        