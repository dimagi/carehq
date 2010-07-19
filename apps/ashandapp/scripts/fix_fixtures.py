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
from django.core import serializers
import sys
            
def run():
    filename = sys.argv[-1]
    
    fin = open(filename, 'r')
    strfile = fin.read()    
    fin.close()
    for obj in serializers.deserialize('json', strfile):               
        try:
            pass
            obj.save()
        except Exception, e:            
            print "%s Exception: %s" % (obj, e)