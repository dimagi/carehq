from datetime import timedelta, datetime
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from pactpatient.enums import PACT_RACE_CHOICES
from pactpatient.updater import update_patient_casexml
from patient.models import CPhone, CAddress
from patient.models import Patient
from receiver.util import spoof_submission
import streets
import names
import random


ADDR_DESCRIPTIONS = ['Home Address', 'Work', 'Friend', 'Mother', 'Parent', "Son's house", "Daugter's", "Friend's house"]
PHONE_DESCRIPTIONS = ['Home', 'Office Phone', 'Cell', 'mobile', "Mom's phone", "Next door neighbor", 'Parent', "Son's phone", "Daugter's", "Friend's house"]

def rzero():
    return str(random.randint(0,9))


def rone():
    return str(random.randint(1,9))

def make_ssn():
    return "Fake-" + rzero() + rzero() + rzero() + "-" + rzero() + rzero() +"-" + rzero() + rzero() + rzero() +rzero()

def make_phone():
    #return rone() + rzero() + rzero() + "-" + rone() + rzero() + rzero() +"-" + rzero() + rzero() + rzero() +rzero()
    return "555-" + rone() + rzero() + rzero() +"-" + rzero() + rzero() + rzero() +rzero()

def raddress():
    return random.choice(streets.descriptors) + " " + random.choice(streets.streetname) + " " + random.choice(streets.suffix)


def make_random_caddress():
    addr = CAddress()
    addr.description = random.choice(ADDR_DESCRIPTIONS)
    addr.street = "%d %s" % (random.randint(1,5000), raddress())
    addr.city = "Metropolis"
    addr.postal_code = "00000"
    addr.state = "MA"
    return addr

def make_random_cphone():
    phone = CPhone()
    phone.description = random.choice(PHONE_DESCRIPTIONS)
    phone.number = make_phone()
    return phone

def adjust_age(dob):
    dy = random.randint(0,15)
    dd = random.randint(0,365)
    directiony = 1 if random.random() > 0.5 else -1
    directiond = 1 if random.random() > 0.5 else -1

    dob = dob + timedelta(days=dd*directiond)
    dob = dob + timedelta(days=365.25*dy * directiony)
    return dob

def make_expiration():
    dy = random.randint(0,5)
    dd = random.randint(0,365)
    directiony = 1 if random.random() > 0.5 else -1
    directiond = 1 if random.random() > 0.5 else -1

    exp = datetime.utcnow() + timedelta(days=dd*directiond)
    exp = exp + timedelta(days=365.25*dy * directiony)
    return exp.date()

new_ids = []
def new_id(pact_id):
    new_id = "R%s%s%s%s" % (rone(), rzero(), rzero(), rzero())
    while True:
        if new_id not in new_ids:
            new_ids.append(new_id)
            break
        new_id = "R%s%s%s%s" % (rone(), rzero(), rzero(), rzero())
    return new_id

    
    

def run():
    patients = Patient.objects.all()
    random.shuffle(names.names)
    for i, pt in enumerate(patients):
        c = pt.couchdoc
        c.last_name = names.names[i]['lastname']
        c.first_name = names.names[i]['firstname']
        c.dob = adjust_age(c.birthdate)
        c.ssn = make_phone()
        c.mass_health_expiration = make_expiration()

        c.race = random.choice(PACT_RACE_CHOICES)[0]

        print names.names[i]

        #c.pact_id = new_id(c.pact_id)
        addr_count = len(c.address)
        phone_count = len(c.phones)
        new_addr = []
        for n in range(0,addr_count):
            addr = make_random_caddress()
            print addr.street
            new_addr.append({"address": "%s %s, %s %s" % (addr.street, addr.city, addr.state, addr.postal_code), 'description': addr.description})
        new_phone = []
        for p in range(0,phone_count):
            phone = make_random_cphone()
            print phone.number
            new_phone.append({'number':phone.number, 'description':phone.description})


        #c.address = new_addr
        #c.phones = new_phone
        print "saving"
        c.save()
        print "saved"

        xml_body = update_patient_casexml(User.objects.all().filter(username='admin')[0], c.case_id, c.pact_id, new_phone, new_addr)
        spoof_submission(reverse("receiver.views.post"), xml_body, hqsubmission=False)

