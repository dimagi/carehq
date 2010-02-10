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

MAX_DELTA=365
PROVIDERS_PER_PATIENT=5
CAREGIVERS_PER_PATIENT = 3
MAX_REVISIONS=5
MAX_INITIAL_CASES = 10


#firstname,middlename,lastname, sex
study_patient_arr = [
["Pat","","Patient","f"],
["Kara","","Thrace","f"],
]


study_caregiver_arr = [
["Dorothy","","Day","f"],
["Clara","","Barton","f"],
]



study_provider_arr = [
["Gregory","House","Internal Medicine","Plainsboro Teaching Hospital"],
["Lisa","Cuddy","Endocrinology","Plainsboro Teaching Hospital"],
["Eric","Foreman","Neurology","Mass General"],
["James","Wilson","Oncologist","Plainsboro Teaching Hospital"],
["Christine","Chapel","Nurse","Boston Medical Center"],
["Alyssa","Ogawa","Triage Nurse","Boston University Medical Center"],
["Allison","Cameron","Immunology","Mass General"],
["Robert","Chase","Radiology","Plainsboro Teaching Hospital"],
["John","Carter","Physical Therapy","Community Rehabilitation Hopsital"],
["Nancy","Apple","Nutritionist","Community Health Center"],
]


def create_user(username='mockuser', password='demouser', firstname=None, lastname=None):    
    user = User()    
    user.username = username
    # here, we mimic what the django auth system does
    # only we specify the salt to be 12345
    salt = '12345'
    hashed_pass = hashlib.sha1(salt+password).hexdigest()
    user.password = 'sha1$%s$%s' % (salt, hashed_pass)
    
    user.first_name = firstname
    user.last_name=lastname
    user.email = '%s_%s@ashand.com' % (firstname, lastname)
    user.set_password(password)
    user.save()
    return user



def create_provider(firstname, lastname, job_title, affiliation):
    firstclean = firstname.replace("'","")
    lastclean = lastname.replace("'","")
    prov = Provider()
    prov.job_title = job_title
    prov.affiliation = affiliation    
    prov.user = create_user(username=firstclean.lower() + "_" + lastclean.lower(), password='demo', firstname=firstname, lastname = lastname)
    prov.save()
    return prov

def create_or_get_provider_role():
    #set some random role.
    role = ProviderRole.ROLE_CHOICES[random.randint(0, len(ProviderRole.ROLE_CHOICES)-1)][0]

#    try:
#        provider_role = ProviderRole.objects.get(role=role)
#    except:    
#    do we neeed to make this a unique instance per person?
    provider_role = ProviderRole()
    provider_role.role = role 
    provider_role.role_description = "unique instance %s" % (uuid.uuid1().hex)
    provider_role.role_notes = "autogenerated from demo_load"
    provider_role.save()
    return provider_role

def create_caregiver_user(firstname, middlename, lastname, sex):
    
    firstclean = firstname.replace("'","")
    lastclean = lastname.replace("'","")
    dob = date(random.randint(1945,1965), random.randint(1,12), random.randint(1,28))
        
    cg = create_user(username=firstclean.lower() + "_" + lastclean.lower(), password='demo', firstname=firstname, lastname=lastname)
    cg.save()
    return cg

def create_patient(firstname, middlename, lastname, sex):
    
    firstclean = firstname.replace("'","")
    lastclean = lastname.replace("'","")
    dob = date(random.randint(1945,1965), random.randint(1,12), random.randint(1,28))
        
    pt = Patient()    
    pt.sex = sex
    pt.dob = dob
    
    pt.user = create_user(username=firstclean.lower() + "_" + lastclean.lower(), password='demo', firstname=firstname, lastname=lastname)
    
    pt.is_primary = True
    pt.save()    
    return pt


def set_random_identifiers(patient):
    for ident in IdentifierType.objects.all():
        if random.random() < 0.33:
            #set some arbitrary somewhat random threshold to skip
            continue
        new_id = PatientIdentifier()
        new_id.id_type = ident
        new_id.patient = patient
        new_id.id_value = uuid.uuid1().hex
        new_id.save()

def create_careteam(patient):
    print "\tCreate care team for patient %s" % patient.user
    team = CareTeam()
    team.patient = patient   
    team.save()
    total_providers = random.randint(0,PROVIDERS_PER_PATIENT)
    all_providers = Provider.objects.all().values_list('id', flat=True)
    prov_arr = [x for x in all_providers]
    random.shuffle(prov_arr)
    print "\tCreated Patient, assigning %d providers" % total_providers
    for num in range(0,total_providers):
        rand_prov_id = prov_arr[num]
        rand_prov = Provider.objects.get(id=rand_prov_id)               
        
        plink = ProviderLink()
        plink.careteam=team
        plink.provider = rand_prov
        
        provider_role = create_or_get_provider_role()
                        
        plink.role = provider_role        
        plink.save()
        
        
    #let's make caregivers now
    total_caregivers = random.randint(0, CAREGIVERS_PER_PATIENT)    
    print "\tCreated Providers, assigning %d caregivers" % (total_caregivers)
    careteam_providers = team.providers.all().values_list('user__id', flat=True)        
    possible_caregivers_qset = User.objects.exclude(id=1).exclude(id=patient.user.id).exclude(id__in=careteam_providers).values_list('id',flat=True)
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
    newcase.status = Status.objects.all()[random.randint(0, Status.objects.all().count() -1)]
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

def work_case(case, user):
    all_descriptions = resolve_arr + working_arr    
    evt = CaseEvent()
    evt.activity = EventActivity.objects.all()[random.randint(0,EventActivity.objects.all().count()-1)]
    evt.case = case
    evt.notes = all_descriptions[random.randint(0, len(all_descriptions) -1 )]
    evt.created_by = user 
    evt.created_date = datetime.utcnow()
    evt.save()

def modify_case(case, user, rev_no):        
    case.last_edit_by = user
    
    #this tests to see if the signal picks up custom attrs added to a model instance.  it does.  not sure how thread safe this will be though.        
    case.edit_comment = 'random change ' + str(uuid.uuid1().hex)
    case.next_action = CaseAction.objects.all()[random.randint(0, CaseAction.objects.all().count() -1)]
    td = timedelta(days=random.randint(0,MAX_DELTA))    
    case.next_action_date = case.next_action_date + td
    case.save()        

def run():
    
    
    #reset the database
    call_command('reset_db', interactive=False)    
    call_command('syncdb', interactive=False)
    
    #load all the demo categories for cases
    load_fixtures()
    
    
#    for ptarr in study_patient_arr:
#        create_patient(ptarr[0],ptarr[1],ptarr[2],ptarr[3])
#    print "Created test patients.  Total %d" % Patient.objects.all().count()
            
#    for ptarr in study_caregiver_arr:
#        create_caregiver_user(ptarr[0],ptarr[1],ptarr[2],ptarr[3])
#    print "Created test caregivers.  Total %d" % Patient.objects.all().count()
        
#    for provarr in study_provider_arr:
        #firstname, lastname, job_title, affiliation        
#        create_provider(provarr[0], provarr[1],provarr[2],provarr[3])
#    print "created all providers"    
    
    
        
        
        

    
    
        
        
        
        
        