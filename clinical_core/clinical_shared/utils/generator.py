#from clinical_core.casetracker.models import *
import pdb
from actorpermission.models.actortypes import BaseActorDocument, ProviderActor, CaregiverActor, PatientActor
from casetracker.models.casecore import Case
from clinical_core.patient.models import *
import uuid
from django.contrib.auth.models import User
import random
from datetime import timedelta, datetime
import string
from django.contrib.webdesign import lorem_ipsum as lorem
from pactpatient.models.pactmodels import PactPatient
from patient import careteam_api
from patient.utils.names import NAMES
from patient.utils.scrambler import make_random_caddress, make_random_cphone
from permissions.models import Actor, Role

DEPARTMENTS = [
    'Emergency Medicine',
    'Interal Medicine',
    'Neurology',
    'Radiation Oncology',
    'ONcology',
    'Radiology',
    'Psychiatry',
    'Urology',
    'General Surgery',
    'Physical Medicine and Rehabilitation',
    'Physical Therapy',
    'Endocrinology',
    'Family Medicine',
    ]

PATIENT_IS_USER_PERCENTAGE = .25
PROVIDER_IS_MULTIPLE_THRESHOLD=.33
PROVIDER_IS_CAREGIVER_THRESHOLD=.03
PROVIDER_IS_PATIENT_THRESHOLD=.01
PATIENT_HAS_MULTIPLE_CAREGIVERS=.33
MAX_PROVIDERS = 7

CREATE_NEW_PERCENTAGE = .1

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
        addr = make_random_caddress()
        ret.append(addr)
    return ret


def generate_phones(num):
    ret = []
    for i in range(num):
        phone = make_random_cphone()
        ret.append(phone)
    return ret

def get_or_create_patient(tenant, user=None, first_name=None, middle_name=None, last_name=None, gender=None):
    """
    Returns a patient document
    """

    if user is None:
        user = get_or_create_user(first_name=first_name, last_name=last_name)

    pt = SimplePatient()
    pt.patient_id = str(random_number(length=10))
    pt.birthdate = datetime.now().date() - (timedelta(days=random.randint(0,60) * 365))

    pt.first_name = user.first_name

    if middle_name == None:
        pt.middle_name = "mock-%s" % (uuid.uuid4().hex[0:10])
    else:
        pt.middle_name = middle_name

    pt.last_name = user.last_name

    if gender == None:
        pt.gender = BasePatient.GENDER_CHOICES[random.randint(0, 1)][0]
    else:
        pt.gender = gender

    addrs = generate_addresses(2)
    phones = generate_phones(3)

    pt.address=addrs
    pt.phones=phones
    pt.notes = "Autogenerated patient"

    pt.save()

    pt_actor = get_or_create_actor(tenant, user, 'patient')
    pt_actor.patient_doc_id = pt._id
    pt_actor.save(tenant, user=user)

    #add the patient actor to the careteam because it needs to be given rights to itself
    patient_role = Role.objects.get_or_create(name='mockPatient')[0]
    careteam_api.add_to_careteam(pt.django_patient, pt_actor.django_actor, patient_role)
    return pt


def get_or_create_user(first_name=None, last_name=None):
    if first_name is None and last_name is None:
        name_choice = random.choice(NAMES)
        first_name = name_choice['first_name']
        last_name = name_choice['last_name']

    user = User()

    username = "%s_%s" % (first_name.replace("'",""), last_name.replace("'",""))
    username=username[0:30].lower()
    user.username=username[0:30].lower()
    try:
        exists = User.objects.get(username=user.username)
        return exists
    except:
        user.first_name = first_name
        user.last_name = last_name
        user.set_password("demo")
        user.save()
    return user

existing_actors = {}
def get_or_create_actor(tenant, user, role_type, title=None, department=None):
    """
    Return a django document
    inputs:
    role_type=string of (provider, caregiver, patient)
    """
    #next see if there are any roles for this user already
    if existing_actors.has_key(user.get_full_name()+role_type):
        django_actor = existing_actors[user.get_full_name()+role_type]
        return django_actor
    else:
        return_actor = generate_actor(tenant, user, role_type,  name=user.get_full_name(), title=title, department=department)
        existing_actors[user.get_full_name()+role_type] = return_actor
    return return_actor

def generate_actor(tenant, user, role_type_string, name=None, title=None, department=None):
    """Helper function to generate a role.
    Parameters:
    User object
    role_type_string (provider, caregiver, patient)
    returns: Actor document of the correct subclass type
    """
    if name is None:
        name=random_text(length=64)
    else:
        name=name

    if role_type_string=='provider':
        if department is None:
            department = random.choice(DEPARTMENTS)
        if title is None:
            title = random_text(length=32)
        doc_nurse = random.random()
        if doc_nurse > .33:
            actor_doc = ProviderActor(name=name, title=title, facility_name=department, notes=lorem.paragraph())
        else:
            actor_doc = ProviderActor(name=name, title=title, facility_name=department, specialty=random_text(), notes=lorem.paragraph())
    elif role_type_string=='caregiver':
        actor_doc = CaregiverActor(name=name, notes=lorem.paragraph(), relation= random.choice(CaregiverActor.RELATIONSHIP_CHOICES)[0])
    elif role_type_string=='patient':
        actor_doc = PatientActor(name=name, notes="Patient Actor autogenerated")

    #pdb.set_trace()
    actor_doc.save(tenant, user=user)
    return actor_doc


def mock_case():
    """Simple test:  Create a case and verify that it exists in the database via the API"""
    #get the basic counts
    user1 = get_or_create_user(always_new=False)
    user2 = get_or_create_user(always_new=False)

    print "Got mock users"
    caregiver_creator = get_or_create_actor(user1, 'caregiver', title_string="some caregiver " + random_word(length=12),  department_string="some department " + random_word(length=12), always_create=False)
    provider_assigned = get_or_create_actor(user2, 'provider', title_string="some provider " + random_word(length=12),  always_create=False)

    print "Got Roles"
    print "Creating Patient..."
    patient = get_or_create_patient(get_or_create_user(always_new=False))
    print "Got Patient"

    subs = Case.__subclasses__()

    print "Generating Case"
    newcase = generate_case(caregiver_creator, lorem.sentence(), lorem.paragraph(), provider_assigned, subtype=subs[random.randrange(0, len(subs))])
    newcase.patient = patient.doc_id
    newcase.save()
    print "Created and saved Case"
    return newcase

def generate_case(creator, description, body, assigned_to, subtype=None):
    if subtype:
        casetype = subtype
    else:
        casetype=Case
    newcase = casetype.create(creator, description, body, assigned_to=assigned_to)
    return newcase

def generate_patient_and_careteam(tenant, team_dictionary=None):
    """
    Bootstrap function to generate a mock patient with a careteam around it.

    Inputs:
    dictonary {
    'patient': [first, middle, last, sex],
    'caregivers': [ [first, last], ...],
    'providers': [ [first, last, title, department/facility], ...],
    }

    returns a tuple (patient_doc, caregiver_actor_docs, provider_actor_docs)
    """

    caregivers = []
    providers = []
    if team_dictionary is not None:
        patient_arr = team_dictionary['patient']
        #user=ptuser
        ptuser = get_or_create_user(first_name=patient_arr[0], last_name=patient_arr[2])
        patient_doc = get_or_create_patient(tenant,
                                            user=ptuser,
                                            first_name=patient_arr[0],
                                            middle_name=patient_arr[1],
                                            last_name=patient_arr[2],
                                            gender=patient_arr[3])


        cg_arr = team_dictionary['caregivers']
        for arr in cg_arr:
            print arr
            cguser = get_or_create_user(first_name=arr[0], last_name=arr[1])
            caregiver_actor = get_or_create_actor(tenant, cguser, 'caregiver')
            caregiver_role = get_or_create_role()
            careteam_api.add_to_careteam(patient_doc.django_patient, caregiver_actor.django_actor, caregiver_role)
            caregivers.append(caregiver_actor)

        prov_arr = team_dictionary['providers']
        first_provider = True
        for arr in prov_arr:
            prov_user = get_or_create_user(first_name=arr[0], last_name=arr[1])
            prov_actor = get_or_create_actor(tenant, prov_user, 'provider', title=arr[2], department=arr[3])
            if first_provider:
                careteam_api.add_to_careteam(patient_doc.django_patient, prov_actor.django_actor, primary_provider_role)
                first_provider=False
            else:
                careteam_api.add_to_careteam(patient_doc.django_patient, prov_actor.django_actor, provider_role)
            providers.append(prov_actor)
    else:
        patient_doc = get_or_create_patient(user=ptuser)

        #next, create caregivers
        if random.random() <= PATIENT_HAS_MULTIPLE_CAREGIVERS:
            caregiver_count = random.randint(1,4)
        else:
            caregiver_count = 1

        for cg in range(caregiver_count):
            cg_actor = generate_actor(tenant, get_or_create_user(),'caregiver')
            patient_doc.add_caregiver(cg_actor)
            caregivers.append(cg_actor)

        max_providers = random.randint(1, MAX_PROVIDERS)
        for cg in range(max_providers):
            provrole = get_or_create_actor(tenant, 'provider', user=get_or_create_user(), title=None, department=None)
            patient_doc.add_provider(provrole)
            providers.append(provrole)

        print "Generated %d providers" % (len(providers))
        print "Generated %d caregivers" % (len(caregivers))
    return (patient_doc, caregivers, providers)



def create_case(self, description, actor, priority, status=None, body=None):
    """Create a case for testing purposes
    """
    if body == None:
        body = "mock body %s" % (uuid.uuid4().hex),
    newcase = Case.objects.new_case(Category.objects.all()[0],
                          actor,
                          description,
                          body,
                          Priority.objects.all()[0],
                          status=Status.objects.all().filter(state_class=constants.CASE_STATE_OPEN)[0],
                          activity=ActivityClass.objects.filter(event_class=constants.CASE_EVENT_OPEN)[0]
                          )
    return newcase