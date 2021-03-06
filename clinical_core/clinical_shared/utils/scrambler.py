from clinical_shared.utils import streets
from patient.models.patientmodels import CAddress, CPhone
import random


ADDR_DESCRIPTIONS = ['Home Address', 'Work', 'Friend', 'Mother', 'Parent', "Son's house", "Daughter's", "Friend's house", 'Neighbor', 'Shelter']
PHONE_DESCRIPTIONS = ['Neighbor', 'Home', 'Office Phone', 'Cell', 'Mobile', "Mom's phone", "Next door neighbor", 'Parent', "Son's phone", "Daughter's", "Friend's house"]

def rzero():
    return str(random.randint(0,9))

def rone():
    return str(random.randint(1,9))

def make_phone():
    return rone() + rzero() + rzero() + "-" + rone() + rzero() + rzero() +"-" + rzero() + rzero() + rzero() +rzero()

def raddress():
    return random.choice(streets.STREET_DESCRIPTORS) + " " + random.choice(streets.STREET_NAMES) + " " + random.choice(
        streets.STREET_SUFFIX)


def make_random_caddress():
    """deprecated address schemadocument generator
    """
    addr = CAddress()
    addr.description = random.choice(ADDR_DESCRIPTIONS)
    addr.street = "%d %s" % (random.randint(1,5000), raddress())
    addr.city = random.choice(["Boston",'Brookline','Cambridge','Somerville','Charlestown','Dorchester','Roxbury','Allston','Brighton','Watertown','Malden','Medford','South Boston','Quincy'])
    addr.postal_code = "00000"
    addr.state = "MA"
    return addr

def make_random_cphone():
    """
    Deprecated phone schemadocument generator
    """
    phone = CPhone()
    phone.description = random.choice(PHONE_DESCRIPTIONS)
    phone.number = make_phone()
    return phone