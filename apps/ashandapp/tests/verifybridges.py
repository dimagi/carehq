from django.test import TestCase
from datetime import datetime
import hashlib
import uuid
from django.contrib.auth.models import User
from casetracker.models import Case, Status, ActivityClass, CaseEvent, Priority, Category
from casetracker import constants
from ashandapp.caseregistry.issue import *


class AshandBridgeTests(TestCase):
    
    def setUp(self):
        print "registering in test"
        from ashandapp.caseregistry.issue import register_category
        register_category()         
        

    def testVerifyIssue(self):        
        bridge = IssueCategory()        
        catmodel = Category.objects.get(slug=bridge.slug)        
        self.assertEqual(bridge.display, catmodel.display)        
        
    def testVerifyStatus(self):     
        bridge = IssueCategory()        
        catmodel = Category.objects.get(slug=bridge.slug)           
        self.assertEqual(5, Status.objects.filter(category=catmodel).count())        
