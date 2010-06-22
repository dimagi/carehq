from datetime import datetime, timedelta, date
import hashlib
from django.contrib.auth.models import User
from casetracker.models import Case, Status, EventActivity, CaseEvent, Priority, Category, CaseAction

from provider.models import Provider
from patient.models import Patient, IdentifierType, PatientIdentifier
from ashandapp.models import CareTeam,ProviderRole,ProviderLink, CaregiverLink, CareRelationship

from demo_issues import issues_arr
from demo_questions import question_arr
from demo_working import working_arr
from demo_resolve_close import resolve_arr

import random
import uuid
from django.core.management import call_command
from demopatients import patient_arr
from demoproviders import provider_arr

from bootstrap import load_fixtures
       

def run():
    
    
    #reset the database
    #call_command('reset_db', interactive=False)    
    #call_command('syncdb', interactive=False)
    
    #load all the demo categories for cases
    load_fixtures()
#    call_command('loaddata','study-config-0')
        
        

    
    
        
        
        
        
        