from clinical_core.casetracker.models import *
from clinical_core.patient.models import *
import uuid
from django.contrib.auth.models import User
import random
from datetime import timedelta, datetime
import string
from django.contrib.webdesign import lorem_ipsum as lorem
from pactpatient.models.pactmodels import PactPatient

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

def get_or_create_patient(user=None, first_name=None, last_name=None, gender=None, always_create=True):
    if not always_create:
        print "Getting existing patient"
        return Patient.objects.all()[random.randrange(0,Patient.objects.all().count())]


    pt = Patient()
    cpt = pt.couchdoc
    cpt.birthdate = datetime.now().date() - (timedelta(days=random.randint(0,60) * 365))
    cpt.pact_id = uuid.uuid1().hex
    cpt.primary_hp = random_word(length=10)

    if first_name == None:
        cpt.first_name = "mock"
    else:
        cpt.first_name = first_name

    if last_name == None:
        cpt.last_name = "mock-%s" % (uuid.uuid1().hex[0:10])
    else:
        cpt.last_name = last_name

    if gender == None:
        cpt.gender = PactPatient.GENDER_CHOICES[random.randint(0, 1)][0]
    else:
        cpt.gender = gender

    addrs = generate_addresses(4)
    phones = generate_phones(4)

    cpt.address=addrs
    cpt.phones=phones

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

    pt.save()
    if user is not None:
        pr = PatientRoleModel(user=user, patient=pt)
        pr.save()
    return pt

def get_or_create_user(first_name=None, last_name=None, always_new=True):
    if always_new == False:
        #if it's false, we will randomly decide whether we want to make a new case or not.
        if random.random() > CREATE_NEW_PERCENTAGE:
            #let's do a 25/75 create/existing split
            print "Returning existing user"
            return User.objects.all()[random.randrange(0,User.objects.all().count())]
        else:
            print "Creating new user"

    user = User()

    if first_name == None:
        user.first_name = uuid.uuid1().hex[0:20]
    else:
        user.first_name = first_name

    if last_name == None:
        user.last_name = uuid.uuid1().hex[0:20]
    else:
        user.last_name = last_name

    username = "%s_%s" % (user.first_name.replace("'",""), user.last_name.replace("'",""))
    user.username=username[0:30].lower()
    try:
        exists = User.objects.get(username=user.username)
        return exists
    except:
       user.save()
    return user

def get_or_create_role(user, role_type, title_string=None, department_string=None, always_create=True):
    #next see if there are any roles for this user already
    existing_roles = Actor.objects.all().filter(user=user)
    role = None

    if always_create == False:
        if random.random() > CREATE_NEW_PERCENTAGE:
            for r in existing_roles:
                #check existing roles and get a match on if the type is the same
                if role_type == 'provider' and (isinstance(r.role_object, TriageNurse) or isinstance(r.role_object, CHW) or isinstance(r.role_object, Doctor)):
                    role = r
                    break
                elif role_type == 'caregiver' and isinstance(r.role_object, Caregiver):
                    role = r
                    break
                elif role_type == 'patient' and isinstance(r.role_object, PatientRoleModel):
                    role = r
                    break
            print "\tLooped through %d existing roles" % (existing_roles.count())


    if role == None:
        print "\tGenerating new role"
        role = generate_role(user, role_type, title_string=title_string, department_string=department_string)
    else:
        print "\tUsing existing role"

    return role



def generate_role(user, role_type_string, title_string=None, department_string=None):
    """Helper function to generate a role.
    Parameters:
    User object
    role_type_string (provider, caregiver, patient)
    returns: Actor object of the correct subclass type
    """
    if title_string == None:
        title=random_text(length=64)
    else:
        title=title_string


    if department_string == None:
        department = random_text(length=64)
    else:
        department = department_string

    if role_type_string=='provider':
        doc_nurse = random.random()
        if doc_nurse > .33:
            role = TriageNurse(user=user, title=title, department=department)
            role.save()
        else:
            role = Doctor(user=user, title=title, department=department, specialty=random_text(length=64))
            role.save()
    elif role_type_string=='caregiver':
        role = Caregiver(user=user, notes=random_text(128), relationship_type= Caregiver.RELATIONSHIP_CHOICES[random.randint(0, len(Caregiver.RELATIONSHIP_CHOICES)-1)])
        role.save()
    elif role_type_string=='patient':
        role = PatientRoleModel(user=user)
    return role


def mock_case():
    """Simple test:  Create a case and verify that it exists in the database via the API"""
    #get the basic counts
    user1 = get_or_create_user(always_new=False)
    user2 = get_or_create_user(always_new=False)

    print "Got mock users"
    caregiver_creator = get_or_create_role(user1, 'caregiver', title_string="some caregiver " + random_word(length=12),  department_string="some department " + random_word(length=12), always_create=False)
    provider_assigned = get_or_create_role(user2, 'provider', title_string="some provider " + random_word(length=12),  always_create=False)

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

#def generate_actor(user, actor_type, title_string=None, department_string=None, always_create=True):
#    role = generate_role(user, actor_type,title_string=title_string, department_string=department_string)
#    act = Actor.objects.create_actor(role)
#    return act

def generate_patient_and_careteam(team_dictionary=None):
    """Bootstrap function to generate a mock patient with a careteam around it.
    Returns a tuple of (patient (instance), caregivers (queryset), providers (queryset))"""

    #first create the patient
    if random.random() <= PATIENT_IS_USER_PERCENTAGE:
        ptuser = get_or_create_user()
    else:
        ptuser = None

    caregivers = []
    providers = []
    if team_dictionary != None:
        patient_arr = team_dictionary['patient']
        patient = get_or_create_patient(user=ptuser, first_name=patient_arr[0], last_name=patient_arr[2], gender=patient_arr[3])
        cg_arr = team_dictionary['caregivers']
        for arr in cg_arr:
            cguser = get_or_create_user(first_name=arr[0], last_name=arr[1])
            cgrole = get_or_create_role(cguser, 'caregiver', None, None)
            patient.add_caregiver(cgrole)
            caregivers.append(cgrole)

        prov_arr = team_dictionary['providers']
        for arr in prov_arr:
            provuser = get_or_create_user(first_name=arr[0], last_name=arr[1])
            provrole = get_or_create_role(provuser, 'provider', arr[2], arr[3])
            patient.add_provider(provrole)
            providers.append(provrole)
    else:
        patient = get_or_create_patient(user=ptuser)

        #next, create caregivers
        if random.random() <= PATIENT_HAS_MULTIPLE_CAREGIVERS:
            caregiver_count = random.randint(1,4)
        else:
            caregiver_count = 1

        for cg in range(caregiver_count):
            cg_actor = generate_actor(get_or_create_user(), 'caregiver')
            patient.add_caregiver(cg_actor)
            caregivers.append(cg_actor)

        max_providers = random.randint(1, MAX_PROVIDERS)
        for cg in range(max_providers):
            provrole = get_or_create_role(get_or_create_user(), 'provider', None, None)
            patient.add_provider(provrole)
            providers.append(provrole)

        print "Generated %d providers" % (len(providers))
        print "Generated %d caregivers" % (len(caregivers))
    return (patient, caregivers, providers)



def create_case(self, description, actor, priority, status=None, body=None):
    """Create a case for testing purposes
    """
    if body == None:
        body = "mock body %s" % (uuid.uuid1().hex),
    newcase = Case.objects.new_case(Category.objects.all()[0],
                          actor,
                          description,
                          body,
                          Priority.objects.all()[0],
                          status=Status.objects.all().filter(state_class=constants.CASE_STATE_OPEN)[0],
                          activity=ActivityClass.objects.filter(event_class=constants.CASE_EVENT_OPEN)[0]
                          )
    return newcase