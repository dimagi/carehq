from django.test import TestCase
from datetime import datetime
import hashlib
import uuid
from django.contrib.auth.models import User
from casetracker.models import Case, Status, EventActivity, CaseEvent, Priority, Category
from careplan.models import *



class EventActivityVerificationTest(TestCase):
    fixtures = [
                '0-caseaction.json',
                '1-category.json',
                '2-eventactivity.json',
                '3-priority.json',
                '4-status.json',
                ]

    #todo, create arbitrarily deep careplan and generate an instance of it.  need to check the recursive
    #copy system
    def setUp(self):
        pass

    def _testCreateCase(self):        
        oldcasecount = Case.objects.all().count()
        oldevents = CaseEvent.objects.all().count()
        
        
        user = User.objects.get(username='mockuser')
        newcase = Case()
        newcase.description = "this is a case made by the test case"
        newcase.opened_by = user
        newcase.assigned_date = datetime.utcnow()
        newcase.assigned_to = user
        
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
    
    
    