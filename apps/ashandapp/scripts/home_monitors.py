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
from casetracker import constants

MAX_DELTA=365
PROVIDERS_PER_PATIENT=5
CAREGIVERS_PER_PATIENT = 3
MAX_REVISIONS=5
MAX_INITIAL_CASES = 10

def create_homemonitoring_alert(num_alerts, careteam):
    alerts = [
("Patient weight has dropped over 10 lbs","Please contact patient immediately for dietary assessment", 1),
("Patient has been vomiting more than 48 hours after treatment","Please contact patient immediately - if non responsive, call for an ambulance",1),
("Patient has shortness of breath/chest pain","Contact patient immediately and recommend checking in to ED",1),
("Patient has pain in a new place","Call patient for pain assessment",4),
("Patient has severe nausea", "Contact patient immediately",3),
("Patient is experiencing hearing loss","Check for other neuro side effects",4),
("Patient has not submitted daily measurements","Contact patient and caregiver immediately",1),
("Patient daily measurements incomplete", "Advise patient to retest full results",4)              
              ]
    random.shuffle(alerts)
    
    for n in range(0, num_alerts):
        newcase = Case()
       
        newcase.description = "%s" % alerts[n][0]
        newcase.body = alerts[n][1]
        
        print "\tNew Alert: %s" % alerts[n][0]
        newcase.category = Category.objects.get(category='HomeMonitoring')
        newcase.opened_by = User.objects.get(id=2) # the hard coded ashand system messages
        newcase.last_edit_by = User.objects.get(id=2) # the hard coded ashand system messages
        newcase.assigned_to = careteam.primary_provider.user
        newcase.next_action = CaseAction.objects.get(id=3) #follow up
        newcase.status = Status.objects.all().filter(category=newcase.category).filter(state_class=constants.CASE_STATE_OPEN)[0]
        
        td = timedelta(hours=alerts[n][2])
        newcase.next_action_date = datetime.utcnow() + td
        newcase.priority= Priority.objects.all()[0]
        newcase.save()
        careteam.add_case(newcase)

def run():
    
    
    for team in CareTeam.objects.all():
        num_alerts = random.randint(3,6)
        print "creating %d alerts" % num_alerts
        create_homemonitoring_alert(num_alerts, team)
    