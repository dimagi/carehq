from clinical_core.actors.models import *
from clinical_core.casetracker.models import *
from autofixture import AutoFixture as af
from clinical_core.patient.models import *
import uuid
from django.contrib.auth.models import User
import random
from datetime import timedelta, datetime

PATIENT_IS_USER_PERCENTAGE = .25
PROVIDER_IS_MULTIPLE_THRESHOLD=.33
PROVIDER_IS_CAREGIVER_THRESHOLD=.03
PROVIDER_IS_PATIENT_THRESHOLD=.01
PATIENT_HAS_MULTIPLE_CAREGIVERS=.33

MAX_PROVIDERS = 7



def generate_patient(user=None):
    if IdentifierType.objects.all().count() == 0:
        af(IdentifierType).create(4)
        
    
    pt = Patient()        
    pt.sex = Patient.GENDER_CHOICES[random.randint(0, 1)][0]    
    pt.dob = datetime.now().date() - (timedelta(days=random.randint(0,60) * 365))
    pt.notes = "randomly generated"
    
    
    #pt = af(Patient, generate_m2m={'address': (1,3)}).create(1)[0]
    if user != None:
        pt.user = user    
    pt.save()
    
    addrs = af(Address).create(random.randint(1,3))
    for addr in addrs:
        pt.address.add(addr)
    
    ids = af(PatientIdentifier).create(random.randint(1,3))
    for id in ids:
        pt.identifiers.add(id)
        
    return pt

def generate_user():
    #print "********************Generate user:"
    #print User.objects.all().count()
    #user = af(User,generate_fk=True).create(1)[0]
    user = User()
    user.first_name = uuid.uuid1().hex[0:20]
    user.last_name = uuid.uuid1().hex[0:20]
    user.username="mockuser" + str(User.objects.all().count())
    user.save()
    #print user.username
    #print User.objects.all().count()    
    return user
    
def generate_actor(user, type):    
    act = Actor()
    act.user = user
    if type=='provider':
        doc_nurse = random.random()
        if doc_nurse > .33:
            role = af(TriageNurse, generate_fk=True).create(1)[0]
        else:
            role = af(Doctor, generate_fk=True).create(1)[0]
    
    elif type=='caregiver':
        role = af(Caregiver, generate_fk=True).create(1)[0]
    
    act.role = role    
    act.save()
    #print "Generated actor with role %s: %s" % (type, role)
    return act

def generate_patient_and_careteam():
    #first create the patient
    if random.random() <= PATIENT_IS_USER_PERCENTAGE:
        ptuser = generate_user()
    else:
        ptuser = None    
    patient = generate_patient(user=ptuser)
    caregivers = []
    providers = []
    
    
    #next, create caregivers
    if random.random() <= PATIENT_HAS_MULTIPLE_CAREGIVERS:
        caregiver_count = random.randint(1,4)
    else:
        caregiver_count = 1
    
    for cg in range(0, caregiver_count):
        cg_user = generate_user() 
        cg_actor = generate_actor(cg_user, "caregiver")
        
        pal = PatientActorLink(patient=patient, actor=cg_actor, active=True)
        pal.save()
        
        
        caregivers.append(cg_actor)
        
    max_providers = random.randint(1, MAX_PROVIDERS)
    
    for cg in range(0, max_providers):
        pr_user = generate_user() 
        pr_actor = generate_actor(cg_user, "provider")
        
        pal = PatientActorLink(patient=patient, actor=pr_actor, active=True)
        pal.save()
        
        providers.append(pr_actor)
    
    print "Generated %d providers" % (len(providers))
    print "Generated %d caregivers" % (len(caregivers))    
    return (patient, caregivers, providers)
    
    
    
        
        
    
