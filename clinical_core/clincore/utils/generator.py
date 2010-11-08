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
    for i in range(num):
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
    for i in range(num):
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
    pt.doc_id = str(cpt._id.strip())
    pt.save()
    return pt

def generate_user():
    user = User()
    user.first_name = uuid.uuid1().hex[0:20]
    user.last_name = uuid.uuid1().hex[0:20]
    user.username="mockuser" + str(User.objects.all().count())
    user.save()
    return user


def generate_role(user, role_type_string):
    """Helper function to generate a role.
    Parameters:
    User object
    role_type_string (provider, caregiver)
    returns: Role object of the correct subclass type
    """
    if role_type_string=='provider':
        doc_nurse = random.random()
        if doc_nurse > .33:
            role = TriageNurse(user=user, title=random_text(length=64), department=random_text(length=64))
            role.save()
        else:
            role = Doctor(user=user, title=random_text(length=64), department=random_text(length=64), specialty=random_text(length=64))
            role.save()
    elif role_type_string=='caregiver':
        role = Caregiver(user=user, notes=random_text(128), relationship_type= Caregiver.RELATIONSHIP_CHOICES[random.randint(0, len(Caregiver.RELATIONSHIP_CHOICES)-1)])
        role.save()
    return role
    
def generate_actor(user, role_type):
    role = generate_role(user, role_type)
    act = Actor.objects.create_actor(role)
    return act

def generate_patient_and_careteam():
    """Bootstrap function to generate a mock patient with a careteam around it.
    Returns a tuple of (patient (instance), caregivers (queryset), providers (queryset))"""


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
    
    for cg in range(caregiver_count):
        cg_actor = generate_actor(generate_user(), 'caregiver')
        patient.add_caregiver(cg_actor)
        caregivers.append(cg_actor)

    max_providers = random.randint(1, MAX_PROVIDERS)
    for cg in range(max_providers):
        provactor = generate_actor(generate_user(), 'provider')
        patient.add_provider(provactor)
        providers.append(provactor)
    
    print "Generated %d providers" % (len(providers))
    print "Generated %d caregivers" % (len(caregivers))    
    return (patient, caregivers, providers)



def create_case(self, description, actor, priority, status=None):
    """Create a case for testing purposes
    """
    newcase = Case.objects.new_case(Category.objects.all()[0],
                          actor,
                          description,
                          "mock body %s" % (uuid.uuid1().hex),
                          Priority.objects.all()[0],
                          status=Status.objects.all().filter(state_class=constants.CASE_STATE_OPEN)[0],
                          activity=ActivityClass.objects.filter(event_class=constants.CASE_EVENT_OPEN)[0]
                          )
    return newcase