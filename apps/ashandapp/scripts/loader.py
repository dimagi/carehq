import random

from datetime import datetime, timedelta
from casetracker.models import Category, Case, Priority, Status, ActivityClass, CaseEvent
from casetracker import constants
from ashandapp.models import CareTeam
from patient.models import Patient
from django.contrib.auth.models import User 
from staticdata.example_interactions import interactions_arr, long_cases

def load_interaction(careteam, interaction_arr):
    """
    works through the entire array to simulate the case lifecycle
    """
    startdelta = timedelta(days=random.randint(1,7)) #sometime in the past week
    
    
    main_info = interaction_arr[0:4]
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
        print "no creator, wtf: " + str(interaction_arr)
    newcase.opened_by = creator    
    newcase.opened_date = datetime.utcnow() - startdelta
    newcase.last_edit_by = creator
    newcase.last_edit_date = newcase.opened_date
    newcase.status = Status.objects.all().filter(category=newcase.category).filter(state_class=constants.CASE_STATE_OPEN)[0]

    newcase.assigned_to = careteam.providers.all()[random.randint(0,careteam.providers.all().count()-1)].user
    newcase.assigned_date = newcase.opened_date 

    newcase.priority = Priority.objects.all()[random.randint(0, Priority.objects.all().count() -1)]    
    newcase.save(unsafe=True)
    careteam.add_case(newcase)
    
    
    
    subarr = interaction_arr[4:]
    while len(subarr) >= 3:
        resp = subarr[0].strip()
        src = subarr[1].lower().strip()
        evt = subarr[2].lower().strip()
        
        if resp == '' and src == '' and evt == '':
            break
        responder=None
        if src.lower() == 'provider':
            responder = careteam.primary_provider.user            
        elif src.lower() == 'caregiver':
            responder = careteam.caregivers.all()[0]
        elif src.lower() == 'patient':
            responder = careteam.patient.user
        if responder == None:
            print "wtf: " + str(subarr)
        
        evt = CaseEvent()
        evt.case = newcase
        if resp.count("%s") == 1:
            resp = resp % careteam.patient.user.first_name
        evt.notes = resp
        evt.activity = ActivityClass.objects.filter(category=newcase.category)\
            .filter(event_class=constants.CASE_EVENT_COMMENT)[0]
        evt.created_by = responder
        startdelta = startdelta - timedelta(minutes=random.randint(4,480))
        evt.created_date = datetime.utcnow() - startdelta
        evt.save(unsafe=True)
            
        
        if len(subarr[3:]) >= 3:
            subarr = subarr[3:]
        else:
            break

def assign_interactions(careteam, num_encounters):
    """
    For a given careteam, generate an arbitrary number of interactions from the interactions_arr
    """
    random.shuffle(interactions_arr)
    interactions = interactions_arr[0:num_encounters]
        
    for interaction in interactions:  
        load_interaction(careteam, interaction)


def add_long_cases():
    """
    Specific hack to add a long case to Pat Patient's caseload
    """
    pt = Patient.objects.get(user__first_name='Pat', user__last_name='Patient')
    ct = CareTeam.objects.get(patient=pt)
    for c in long_cases:
        load_interaction(ct, c)
        