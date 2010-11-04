from clinical_core.actors.models import *
from clinical_core.casetracker.models import *
from autofixture import AutoFixture as af
from clinical_core.patient.models import *
import uuid
from django.contrib.auth.models import User
import random
from datetime import timedelta, datetime
import string

PATIENT_IS_USER_PERCENTAGE = .25
PROVIDER_IS_MULTIPLE_THRESHOLD=.33
PROVIDER_IS_CAREGIVER_THRESHOLD=.03
PROVIDER_IS_PATIENT_THRESHOLD=.01
PATIENT_HAS_MULTIPLE_CAREGIVERS=.33
MAX_PROVIDERS = 7

def generate_random_string(length=8, source=string.ascii_letters):
    return ''.join([random.choice(source) for i in range(length)])

def random_word(length=8):
    return generate_random_string(length=length, source=string.ascii_letters)

def random_text(length=64):
    return generate_random_string(length=length, source=string.ascii_letters + string.digits + string.whitespace + string.punctuation)

def random_number(length=10):
    return generate_random_string(length=length, source=string.digits)

def generate_addresses(num):
    ret = []
    for i in range(0,num):
        addr = CAddress()
        addr.description = random_text(length=16)
        addr.street = random_text(length=32)
        addr.city = random_word(length=12)
        addr.state = random_word(length=12)
        addr.postal_code = random_number(length=5)
        ret.append(addr)
    return ret


def generate_phones(num):
    ret = []
    for i in range(0,num):
        phone = CPhone()
        phone.postal_code = random_number(length=5)
        phone.is_default = True
        phone.number = "%s-%s-%s" % (random_number(length=3), random_number(length=3), random_number(length=4))
        phone.description = random_text(length=16)
        ret.append(phone)
    return ret

def generate_patient(user=None):
    cpt = CPatient()
    cpt.gender = CPatient.GENDER_CHOICES[random.randint(0, 1)][0]
    cpt.birthdate = datetime.now().date() - (timedelta(days=random.randint(0,60) * 365))
    cpt.pact_id = random_word(length=10)
    cpt.primary_hp = random_word(length=10)

    cpt.first_name = "mock"
    cpt.last_name = "mock-%s" % (uuid.uuid1().hex[0:10])

    addrs = generate_addresses(4)
    phones = generate_phones(4)

#    cpt.django_uuid = StringProperty() #the django uuid of the patient object
#    cpt.pact_id = StringProperty(required=True)
#    cpt.first_name = StringProperty(required=True)
#    cpt.middle_name = StringProperty()
#    cpt.last_name = StringProperty(required=True)
#    cpt.primary_hp = StringProperty(required=True)
#    cpt.arm = StringProperty()
#    cpt.birthdate = DateProperty()
#    cpt.patient_id = StringProperty()
#    cpt.address = SchemaListProperty(CAddress)
#    cpt.phones = SchemaListProperty(CPhone)
#    cpt.art_regimen = StringProperty()
#    cpt.non_art_regimen = StringProperty()
#    cpt.date_modified = DateTimeProperty(default=datetime.utcnow)

    cpt.save()
    pt = Patient()
    pt.doc_id = cpt._id
    pt.save()
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
