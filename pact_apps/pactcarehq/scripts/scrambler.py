from patient.models import CPhone, CAddress
from patient.models import Patient
import streets
import names
import random

def rzero():
    return str(random.randint(0,9))


def rone():
    return str(random.randint(1,9))

def make_phone():
    return rone() + rzero() + rzero() + "-" + rone() + rzero() + rzero() +"-" + rzero() + rzero() + rzero() +rzero()

def raddress():
    return random.choice(streets.descriptors) + " " + random.choice(streets.streetname) + " " + random.choice(streets.suffix)

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
            addr = CAddress()
            addr.description = c.address[n].description
            addr.street = "%d %s" % (random.randint(1,5000), raddress())
            addr.city = "Metropolis"
            addr.postal_code = "00000"
            addr.state = "MA"
            new_addr.append(addr)
            print addr.street
        new_phone = []
        for p in range(0,phone_count):
            phone = CPhone()
            phone.description = c.phones[p].description
            phone.number = make_phone()
            print phone.number
            new_phone.append(phone)

        c.address = new_addr
        c.phones = new_phone
        c.save()
