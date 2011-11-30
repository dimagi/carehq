from datetime import datetime, timedelta
import random_inject
from casetracker.models import Case
from django.contrib.auth.models import User
from .demo import DEMO_CARETEAMS, DEMO_CASES
from clinical_shared.utils import generator
import random
from django.core.management import call_command
from casetracker import constants

def inject_case_data(patient, event_arr):
    """
    Pull data from the event_arr and assign it to a patient if they were new inbound triage cases
    """    
    print "Adding monitoring event to patient %s" % (patient)
    startdelta = timedelta(minutes=random_inject.randint(1,200)) #sometime in the past 3
    main_info = event_arr[0:4]            
    category_txt = main_info[0].strip()            
    title = main_info[1].strip()
    body = main_info[2].strip()
    source = main_info[3].strip()

    if title.count("%s") == 1:
        title = title % patient
    if body.count("%s") == 1:
        body = body % patient\

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
        newcase.priority = Priority.objects.all()[random_inject.randint(0, Priority.objects.all().count() -1)]
    newcase.save(unsafe=True)
    careteam.add_case(newcase)



def generate_triage():
    """
    Pull data from the triage_arr and randomly assign them to patients as if they were new inbound triage cases
    """    
    
    careteams = CareTeam.objects.all()    
    
    for careteam in careteams:
        max_encounters = random_inject.randint(1,2)
        random_inject.shuffle(triage_arr)
        print "Adding %d new triage events to patient %s" % (max_encounters, careteam.patient.user.title())
        for enc in range(0,max_encounters):    
            inject_case_data(careteam, triage_arr[enc])


            
import sys
def run():
    """Inject a standard set of data for demo/trial demonstration.
    """
    #establish the patient and careteams.
    for t in DEMO_CARETEAMS:
        print t['patient']
        pt, caregivers, providers = generator.generate_patient_and_careteam(team_dictionary=t)
        all_people  = caregivers+providers

        for i in range(0,10):
            arr = DEMO_CASES.pop()
            actor_creator = random.choice(all_people)
            caregiver_creator = random.choice(all_people)
            provider_assigned = random.choice(providers)
            description = arr[0]
            body = arr[1]
            newcase = Case.objects.new_case("question",
                              actor_creator,
                              arr[0],
                              arr[1],
                              constants.PRIORITY_CHOICES[0][0],
                              patient=pt,
                              status=constants.STATUS_CHOICES[0][0],
                              activity=constants.CASE_EVENT_CHOICES[0][0],
                              )
            newcase.patient=pt
            newcase.save(activity=constants.CASE_EVENT_EDIT)


#
#    #establish initial data
#    inject_case_data(CareTeam.objects.filter(patient__user__username='william_adama')[0],\
#                        ["ashand-question","Patient daily measurements incomplete","Missing data alert: Missing weight and temperature","Home Monitor"])
#    inject_case_data(CareTeam.objects.filter(patient__user__username='william_adama')[0],\
#                        ["ashand-issue","%s has a runny nose","is it bad?","Caregiver"])
#
#    inject_case_data(CareTeam.objects.filter(patient__user__username='curzon_dax')[0],\
#                        ["ashand-issue","urgent","What order should I instruct the patient to take their anti nausea meds?","Caregiver"])
#    inject_case_data(CareTeam.objects.filter(patient__user__username='curzon_dax')[0],\
#                        ["ashand-issue","not feeling well","%s has been reporting severe constipation the past few days","Caregiver"])
#    inject_case_data(CareTeam.objects.filter(patient__user__username='curzon_dax')[0],\
#                        ["ashand-issue","help","Do I need to fast before my next visit?","patient"])
#
#    inject_case_data(CareTeam.objects.filter(patient__user__username='jadzia_dax')[0],\
#                        ["ashand-issue","not a big deal","Do I need to take all these meds you gave me?","Caregiver"])
#
#    inject_case_data(CareTeam.objects.filter(patient__user__username='pat_patient')[0],\
#                        ["ashand-issue","bleeding gums","was about to brush my teeth when I saw it","patient"],)
#    inject_case_data(CareTeam.objects.filter(patient__user__username='pat_patient')[0],\
#                        ["ashand-issue","more skin problems for %s","Thanks for the tip on the last skin issue!","caregiver"],)
#
#    inject_case_data(CareTeam.objects.filter(patient__user__username='joseph_sisko')[0],\
#                        ["ashand-issue","%s has severe diarrhea","%s was up most of the night, was able to stay hydrated, but am worried.","Caregiver"])
#    inject_case_data(CareTeam.objects.filter(patient__user__username='joseph_sisko')[0],\
#                        ["ashand-issue","fever","at what temperature should I know to call for help?","patient"])
#    inject_case_data(CareTeam.objects.filter(patient__user__username='joseph_sisko')[0],\
#                        ["ashand-issue","is it bad?","not sure if this is hives or a rash","Caregiver"])
#
#    #inject home monitoring data
#    inject_case_data(CareTeam.objects.filter(patient__user__username='benjamin_sisko')[0],\
#                        ["ashand-question","Patient has not submitted daily measurements","Missing data alert","Home Monitor"])
#    inject_case_data(CareTeam.objects.filter(patient__user__username='deanna_troi')[0],\
#                        ["ashand-question","Patient has vomited 2 times in the past 24 hours","Daily reading alert","Home Monitor"])
#
#    num_cases= random_inject.randint(0,5)
#    print "\tgenerating %d baseline interactions" % (num_cases)
#    #assign_interactions(careteam, num_cases)
#    #add_long_cases() #adds the longer commented case
