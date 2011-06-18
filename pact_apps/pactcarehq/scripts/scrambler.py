from patient.models import CPhone, CAddress
from patient.models import Patient
import streets
import names
import random


ADDR_DESCRIPTIONS = ['Home Address', 'Work', 'Friend', 'Mother', 'Parent', "Son's house", "Daugter's", "Friend's house"]
PHONE_DESCRIPTIONS = ['Home', 'Office Phone', 'Cell', 'mobile', "Mom's phone", "Next door neighbor", 'Parent', "Son's phone", "Daugter's", "Friend's house"]

def rzero():
    return str(random.randint(0,9))


def rone():
    return str(random.randint(1,9))

def make_phone():
    return rone() + rzero() + rzero() + "-" + rone() + rzero() + rzero() +"-" + rzero() + rzero() + rzero() +rzero()

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

def run():
    patients = Patient.objects.all()
    random.shuffle(names.names)
    for i, pt in enumerate(patients):
        c = pt.couchdoc
        c.last_name = names.names[i]['lastname']
        c.first_name = names.names[i]['firstname']
        print names.names[i]

        addr_count = len(c.address)
        phone_count = len(c.phones)
        new_addr = []
        for n in range(0,addr_count):
            addr = make_random_caddress()
            new_addr.append(addr)
            print addr.street
        new_phone = []
        for p in range(0,phone_count):
            phone = make_random_cphone()
            print phone.number
            new_phone.append(phone)

        c.address = new_addr
        c.phones = new_phone
        c.save()
