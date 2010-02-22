from datetime import datetime, timedelta, date
import hashlib
from django.contrib.auth.models import User
import random
import uuid


from casetracker.models import Case, Status, EventActivity, CaseEvent, Priority, Category, CaseAction

from provider.models import Provider
from patient.models import Patient, IdentifierType, PatientIdentifier
from ashandapp.models import CareTeam,ProviderRole,ProviderLink, CaregiverLink, CareRelationship

from demo_issues import issues_arr
from demo_questions import question_arr
from demo_working import working_arr
from demo_resolve_close import resolve_arr


from example_interactions import interactions_arr, triage_arr

from django.core.management import call_command
from demopatients import patient_arr
from demoproviders import provider_arr

from bootstrap import load_fixtures

from casetracker import constants

from factory import create_user, create_provider, create_or_get_provider_role, create_patient, set_random_identifiers



def generate_triage():
    
    #loop through all patients
    careteams = CareTeam.objects.all()
    
    
    for careteam in careteams:
        max_encounters = random.randint(1,3)    
        random.shuffle(triage_arr)
        print "Adding %d new triage events to patient %s" % (max_encounters, careteam.patient.user.get_full_name()) 
        for enc in range(0,max_encounters):    
            startdelta = timedelta(hours=random.randint(1,12)) #sometime in the past 12 hours
            main_info = triage_arr[enc][0:4]            
            category_txt = main_info[0].strip()            
            title = main_info[1].strip()
            body = main_info[2].strip()
            source = main_info[3].strip()
        
            if title.count("%s") == 1:
                title = title % careteam.patient.user.first_name
            if body.count("%s") == 1:
                body = body % careteam.patient.user.first_name
            
            newcase = Case()
            newcase.description = title
            newcase.body = body
            newcase.category = Category.objects.get(category=category_txt)
            
            creator=None
            if source.lower() == 'provider':
                creator = careteam.primary_provider.user            
            elif source.lower() == 'caregiver':
                creator = careteam.caregivers.all()[0]
            elif source.lower() == 'patient':
                creator = careteam.patient.user
            elif source.lower() == 'home monitor':
                creator = User.objects.get(username ='ashand-system')
            
            if creator == None:
                print "no creator, wtf"
            newcase.opened_by = creator    
            newcase.opened_date = datetime.utcnow() - startdelta
            newcase.last_edit_by = creator
            newcase.last_edit_date = newcase.opened_date
            newcase.status = Status.objects.all().filter(category=newcase.category).filter(state_class=constants.CASE_STATE_NEW)[0]
        
            newcase.assigned_to = careteam.primary_provider.user
            newcase.assigned_date = newcase.opened_date 
        
            newcase.priority = Priority.objects.all()[random.randint(0, Priority.objects.all().count() -1)]    
            newcase.next_action = CaseAction.objects.all()[2]
            newcase.next_action_date = newcase.opened_date + timedelta(hours=newcase.priority.id)        
            newcase.save(unsafe=True)
            careteam.add_case(newcase)
            
            
def run():
    generate_triage()