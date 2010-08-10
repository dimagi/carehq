from datetime import datetime, timedelta, date
import hashlib
from django.contrib.auth.models import User
import random
import uuid


from casetracker.models import Case, Status, EventActivity, CaseEvent, Priority, Category, CaseAction

from provider.models import Provider
from patient.models import Patient, IdentifierType, PatientIdentifier
from ashandapp.models import CareTeam,ProviderRole,ProviderLink, CaregiverLink, CareRelationship

from staticdata.example_interactions import interactions_arr, triage_arr

from django.core.management import call_command
from staticdata.demo_patients import patient_arr
from staticdata.demo_providers import provider_arr

from casetracker import constants

from factory import create_user, create_provider, create_or_get_provider_role, create_patient, set_random_identifiers
from loader import load_interaction, assign_interactions, add_long_cases

def inject_casemonitor(careteam, event_arr):
    """
    Pull data from the triage_arr and randomly assign them to patients as if they were new inbound triage cases
    """    
    print "Adding monitoring event to patient %s" % (careteam.patient.user.get_full_name()) 
    startdelta = timedelta(minutes=random.randint(1,200)) #sometime in the past 3
    main_info = event_arr[0:4]            
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
    newcase.category = Category.objects.get(slug=category_txt)
    
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
    newcase.status = Status.objects.all().filter(category=newcase.category).filter(state_class=constants.CASE_STATE_OPEN)[0]

    newcase.assigned_to = careteam.primary_provider.user
    newcase.assigned_date = newcase.opened_date 

    if source.lower() == 'home monitor':
        newcase.priority = Priority.objects.all()[0]
    else:
        newcase.priority = Priority.objects.all()[random.randint(0, Priority.objects.all().count() -1)]    
    newcase.next_action = CaseAction.objects.all()[2]
    newcase.next_action_date = newcase.opened_date + timedelta(hours=newcase.priority.id)        
    newcase.save(unsafe=True)
    careteam.add_case(newcase)



def generate_triage():
    """
    Pull data from the triage_arr and randomly assign them to patients as if they were new inbound triage cases
    """    
    
    careteams = CareTeam.objects.all()    
    
    for careteam in careteams:
        max_encounters = random.randint(1,2)    
        random.shuffle(triage_arr)
        print "Adding %d new triage events to patient %s" % (max_encounters, careteam.patient.user.get_full_name()) 
        for enc in range(0,max_encounters):    
            inject_casemonitor(careteam, triage_arr[enc])


            
import sys
def run():
    inject_mode = sys.argv[-1]
    
    if inject_mode == 'randomtriage':
        generate_triage()
    elif inject_mode == 'pat':
        print "Loading some case data for pat patient"
        careteam = CareTeam.objects.filter(patient__user__username='pat_patient')[0]
        num = 10
        assign_interactions(careteam, num)
    elif inject_mode == 'historical':
        for careteam in CareTeam.objects.all().exclude(patient__user__username='pat_patient'):
            num_cases= random.randint(0,5)
            print "\tgenerating %d baseline interactions" % (num_cases)
            assign_interactions(careteam, num_cases)
            add_long_cases() #adds the longer commented case
    
    elif inject_mode == 'initial':
        inject_casemonitor(CareTeam.objects.filter(patient__user__username='william_adama')[0],\
                            ["ashand-question","Patient daily measurements incomplete","Missing data alert: Missing weight and temperature","Home Monitor"])
        inject_casemonitor(CareTeam.objects.filter(patient__user__username='william_adama')[0],\
                            ["ashand-issue","%s has a runny nose","is it bad?","Caregiver"])
        
        inject_casemonitor(CareTeam.objects.filter(patient__user__username='curzon_dax')[0],\
                            ["ashand-issue","urgent","What order should I instruct the patient to take their anti nausea meds?","Caregiver"])
        inject_casemonitor(CareTeam.objects.filter(patient__user__username='curzon_dax')[0],\
                            ["ashand-issue","not feeling well","%s has been reporting severe constipation the past few days","Caregiver"])
        inject_casemonitor(CareTeam.objects.filter(patient__user__username='curzon_dax')[0],\
                            ["ashand-issue","help","Do I need to fast before my next visit?","patient"])        
        
        inject_casemonitor(CareTeam.objects.filter(patient__user__username='jadzia_dax')[0],\
                            ["ashand-issue","not a big deal","Do I need to take all these meds you gave me?","Caregiver"])        
        
        inject_casemonitor(CareTeam.objects.filter(patient__user__username='pat_patient')[0],\
                            ["ashand-issue","bleeding gums","was about to brush my teeth when I saw it","patient"],)
        inject_casemonitor(CareTeam.objects.filter(patient__user__username='pat_patient')[0],\
                            ["ashand-issue","more skin problems for %s","Thanks for the tip on the last skin issue!","caregiver"],)
        
        inject_casemonitor(CareTeam.objects.filter(patient__user__username='joseph_sisko')[0],\
                            ["ashand-issue","%s has severe diarrhea","%s was up most of the night, was able to stay hydrated, but am worried.","Caregiver"])
        inject_casemonitor(CareTeam.objects.filter(patient__user__username='joseph_sisko')[0],\
                            ["ashand-issue","fever","at what temperature should I know to call for help?","patient"])
        inject_casemonitor(CareTeam.objects.filter(patient__user__username='joseph_sisko')[0],\
                            ["ashand-issue","is it bad?","not sure if this is hives or a rash","Caregiver"])
            
    elif inject_mode == 'monitoring':
        inject_casemonitor(CareTeam.objects.filter(patient__user__username='benjamin_sisko')[0],\
                            ["ashand-question","Patient has not submitted daily measurements","Missing data alert","Home Monitor"])
        inject_casemonitor(CareTeam.objects.filter(patient__user__username='deanna_troi')[0],\
                            ["ashand-question","Patient has vomited 2 times in the past 24 hours","Daily reading alert","Home Monitor"])
        
        