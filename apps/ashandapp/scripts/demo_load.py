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


from example_interactions import interactions_arr

from django.core.management import call_command
from demopatients import patient_arr
from demoproviders import provider_arr

from bootstrap import load_fixtures

from casetracker import constants

from factory import create_user, create_provider, create_or_get_provider_role, create_patient, set_random_identifiers

MAX_DELTA=365
PROVIDERS_PER_PATIENT=5
CAREGIVERS_PER_PATIENT = 3
MAX_REVISIONS=7
MAX_INITIAL_CASES = 7


def create_careteam(patient):
    print "\tCreate care team for patient %s" % patient.user
    team = CareTeam()
    team.patient = patient   
    team.save()
    total_providers = random.randint(1,PROVIDERS_PER_PATIENT)
    all_providers = Provider.objects.all().values_list('id', flat=True)
    prov_arr = [x for x in all_providers]
    random.shuffle(prov_arr)
    print "\tCreated Patient, assigning %d providers" % total_providers
    first_provider = True
    for num in range(0,total_providers):
        rand_prov_id = prov_arr[num]
        rand_prov = Provider.objects.get(id=rand_prov_id)               
        
        plink = ProviderLink()
        plink.careteam=team
        plink.provider = rand_prov

        if first_provider:
            provider_role = create_or_get_provider_role(is_primary=True)
            first_provider=False
        else:
            provider_role = create_or_get_provider_role(is_primary=False)
                        
        plink.role = provider_role        
        plink.save()
        
        
    #let's make caregivers now
    total_caregivers = random.randint(1, CAREGIVERS_PER_PATIENT)    
    print "\tCreated Providers, assigning %d caregivers" % (total_caregivers)
    careteam_providers = team.providers.all().values_list('user__id', flat=True)
    #possible_caregivers_qset = User.objects.exclude(id=1).exclude(id=patient.user.id).exclude(id__in=careteam_providers).values_list('id',flat=True)
    
    
    all_providers_list = Provider.objects.all().values_list('user__id', flat=True)    
    possible_caregivers_qset = User.objects.exclude(id=1).exclude(id=patient.user.id).exclude(id__in=all_providers_list).values_list('id',flat=True)
    
    possible_caregivers_arr = [x for x in possible_caregivers_qset]    
    random.shuffle(possible_caregivers_arr)
    for num in range(0, total_caregivers):
        caregiver_user = User.objects.get(id=possible_caregivers_arr[num])
        cglink = CaregiverLink()
        cglink.careteam = team
        #cglink.caregiver = caregiver_user
        cglink.user = caregiver_user
        
        relationship = CareRelationship()
        relationship.relationship_type = CareRelationship.RELATIONSHIP_CHOICES[random.randint(0, len(CareRelationship.RELATIONSHIP_CHOICES)-1)][0]
        relationship.notes = ''
        relationship.save()
        
        cglink.relationship = relationship
        cglink.save()
        
        
    
    

def create_case(user, all_users, case_no):    
    newcase = Case()
    newcase.body = "Aliquam ultricies in. Nisl suspendisse ut curabitur nullam, libero magna, id velit quis vitae at. In massa gravida, luctus consequat quis integer, amet amet diam ornare nascetur libero ultrices, lorem urna et. Hac vestibulum, turpis sed sapien cumque. Morbi justo semper lorem gravida, interdum a ante mattis augue at semper, aliquam ridiculus, vulputate repellendus, mi sem in non. Vitae nunc egestas, consectetuer nibh est, ac vestibulum vitae augue ut mauris, ante tortor, velit gravida nisl pellentesque dolor."
    newcase.opened_by = user
    newcase.last_edit_by = user
    
    newcase.assigned_to = all_users[random.randint(0,len(all_users)-1)]
    newcase.assigned_date = datetime.utcnow() - timedelta(days=random.randint(0,720))
    
    #newcase.category = Category.objects.all()[random.randint(0, Category.objects.all().count()-1)]
    newcase.category = Category.objects.all()[random.randint(0, 1)] #right now only support issue/question categories, so only the first two categories
    #newcase.status = Status.objects.all()[random.randint(0, Status.objects.all().count() -1)]
    
    #set the default opened case
    newcase.status = Status.objects.all().filter(category=newcase.category).filter(state_class=constants.CASE_STATE_OPEN)[0]
    
    newcase.priority = Priority.objects.all()[random.randint(0, Priority.objects.all().count() -1)]    
    newcase.next_action = CaseAction.objects.all()[random.randint(0, CaseAction.objects.all().count() -1)]
    
    if newcase.category.category == "Question":
        newcase.description = question_arr[random.randint(0,len(question_arr))-1]
    elif newcase.category.category == "Issue":
        newcase.description = question_arr[random.randint(0,len(question_arr))-1]
    
    #newcase.description = "test case generated - %d" % case_no    
    td = timedelta(days=random.randint(0,MAX_DELTA))
    newcase.next_action_date = datetime.utcnow() + td
    
    newcase.save()
    return newcase


def generate_interactions(careteam, num_encounters):
    """
    For a given careteam, generate an arbitrary number of interactions from the interactions_arr
    """
    random.shuffle(interactions_arr)
    encounters = interactions_arr[0:num_encounters]
    
    #let's clean them up
        
    
    startdelta = timedelta(days=random.randint(1,7)) #sometime in the past week
    
    for encounter in encounters:        
        main_info = encounter[0:4]
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
            print "no creator, wtf: " + str(encounter)
        newcase.opened_by = creator    
        newcase.opened_date = datetime.utcnow() - startdelta
        newcase.last_edit_by = creator
        newcase.last_edit_date = newcase.opened_date
        newcase.status = Status.objects.all().filter(category=newcase.category).filter(state_class=constants.CASE_STATE_OPEN)[0]
    
        newcase.assigned_to = careteam.primary_provider.user
        newcase.assigned_date = newcase.opened_date 
    
        newcase.priority = Priority.objects.all()[random.randint(0, Priority.objects.all().count() -1)]    
        newcase.next_action = CaseAction.objects.all()[2]
        newcase.next_action_date = newcase.opened_date + timedelta(hours=newcase.priority.id)        
        newcase.save(unsafe=True)
        careteam.add_case(newcase)
        
        
        
        subarr = encounter[4:]
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
            evt.activity = EventActivity.objects.filter(category=newcase.category)\
                .filter(event_class=constants.CASE_EVENT_COMMENT)[0]
            evt.created_by = responder
            startdelta = startdelta - timedelta(minutes=random.randint(4,480))
            evt.created_date = datetime.utcnow() - startdelta
            evt.save(unsafe=True)
                
            
            if len(subarr[3:]) >= 3:
                subarr = subarr[3:]
            else:
                break
                
    


def work_case(case, user):
    all_descriptions = resolve_arr + working_arr    
    evt = CaseEvent()
    evt.activity = EventActivity.objects.all()[random.randint(0,EventActivity.objects.all().count()-1)]
    evt.case = case
    evt.notes = all_descriptions[random.randint(0, len(all_descriptions) -1 )]
    evt.created_by = user 
    evt.created_date = datetime.utcnow()
    evt.save()

def resolve_or_close_case(case, user, rev_no):        
    case.last_edit_by = user    
    #this tests to see if the signal picks up custom attrs added to a model instance.  it does.  not sure how thread safe this will be though.        
    action = ""
    close = False
    if random.random() >= .33:
        action = "resolving case"
        close = False
    else:
        action = "closing case"
        close = True
        
    case.edit_comment = action
    case.resolved_by = user
    if close:
        case.status = Status.objects.all().filter(category=case.category).filter(state_class=constants.CASE_STATE_CLOSED)[0]
        case.closed_by = user
    else:
        case.status = Status.objects.all().filter(category=case.category).filter(state_class=constants.CASE_STATE_RESOLVED)[0]
    #case.next_action = CaseAction.objects.all()[random.randint(0, CaseAction.objects.all().count() -1)]
    #td = timedelta(days=random.randint(0,MAX_DELTA))    
    #case.next_action_date = case.next_action_date + td    
    case.save()        

def run():
    
    #Demo loading script!
    
    #reset the database
    call_command('reset_db', interactive=False)    
    call_command('syncdb', interactive=False)
    
    #load all the demo categories for cases
    load_fixtures()    
    
    #create patients    
    for ptarr in patient_arr:
        create_patient(ptarr[0],ptarr[1],ptarr[2],ptarr[3])
    print "Created test patients.  Total %d" % Patient.objects.all().count()
        
    for provarr in provider_arr:
        #firstname, lastname, job_title, affiliation        
        create_provider(provarr[0], provarr[1],provarr[2],provarr[3])
    print "created all providers"
    
    
        
    print "Creating care teams..."
    #create careteam around all patients and link providers to them
    for patient in Patient.objects.all():
        create_careteam(patient)
    
    
    #before making the case, we need to get all the user objects of the people in the careteam.
    #first the providers:
    
    revision_no = 0
    for team in CareTeam.objects.all():        
        provs = team.providers.all()
        caregivers = team.caregivers.all()
        users = [team.patient.user]
        #get the user objects from the providers on this careteam
        for prov in provs:
            #when you do an all on the providers, provider objects, so we need to flip over to the User instead.
            users.append(prov.user)
        for cg in caregivers:
            users.append(cg)
        
        num_cases= random.randint(0,10)
        generate_interactions(team, num_cases)
        
        #create fictitious cases and case activity by patients and providers.
        #for num in range(0,MAX_INITIAL_CASES):            
            #case = create_case(users[random.randint(0,len(users)-1)], users, num)
            
            #team.add_case(case)
            #num_revisions = random.randint(0,MAX_REVISIONS)
            #print "New case created for patient %s, case %d" % (team.patient, num)
            #for rev in range(0,num_revisions):
            #    print "\tApplying revision %d - %d" % (rev, revision_no)
            #    modding_user = users[random.randint(0,len(users)-1)]
            #    if random.random() >= .25:
            #        #let's bias towards doing work on a case
            #        work_case(case,modding_user)
            #    else:
            #        resolve_or_close_case(case, modding_user, revision_no)
            #        
            #    revision_no += 1
   
    
    
        
        
        

    
    
        
        
        
        
        