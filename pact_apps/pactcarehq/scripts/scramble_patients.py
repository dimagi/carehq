from patient.models import CPhone, CAddress
from patient.models import Patient


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
