from couchdbkit.exceptions import ResourceNotFound
from casexml.apps.case.models import CommCareCase
from patient.models import Patient
import re

def filter_addr_phone(f):
    if f.lower().startswith('phone') or f.lower().startswith('address'):
        return True
    else:
        return False


def merge_props(lst):
    phonematch = re.compile('Phone(?P<num>\d)(\w*)')
    addressmatch = re.compile('address(?P<num>\d)(\w*)')

    phones = {}
    address = {}

    for key in lst:

        pm = phonematch.match(key)
        am = addressmatch.match(key)
        if pm != None:
            #it's a phone
            num = int(pm.group('num'))
            type = pm.group(2)

            phone_props = phones.get(num-1, ['number'])
            if type != '':
                phone_props.append('description')
            phones[num] = phone_props

        if am != None:
            #it's a phone
            num = int(am.group('num'))
            type = am.group(2)

            addr_props = address.get(num-1, [])
            if type != '':
                addr_props.append('description')
            address[num] = addr_props
    return phones, address


def get_case_phone(num, props, case):
    ret = {}

    if hasattr(case, 'Phone%d' % num):
        ret['number'] = getattr(case, 'Phone%d' % num)
    else:
        return {}

    if hasattr(case, 'Phone%dType' % num):
        ret['description'] = getattr(case, 'Phone%dType' % num)
    else:
        ret['description'] = None
    return ret


def run():
    patients = Patient.objects.all()
    for pt in patients:
        try:
            print "\t###Patient %s" % pt.id
            cpatient = pt.couchdoc
            case_id = cpatient.case_id
            case = CommCareCase.get(case_id)
            prop_keys = case._dynamic_properties.keys()
            addr_keys = filter(filter_addr_phone, prop_keys)

            addr_keys.sort()
            phones, address = merge_props(addr_keys)

            for i, p in enumerate(cpatient.phones):
                print "\t\t### Phone %d ####" % (i)
                if p.number != '':
                    print "\t\tCouchphone: %s: %s" % (p.description, p.number)
                else:
                    pass


                phone_dict = get_case_phone(i+1, phones, case)
                if len(phone_dict.keys()) > 0:
                    print "\t\tCase phone: %s: %s" % (phone_dict['description'], phone_dict['number'])
                else:
                    pass
                    #print "\t\tNo Case Phone"



        except ResourceNotFound, ex:
            print "\t\tNot present"
        except Exception, ex:
            print ex.message
            print ex.__class__
            print "\t\t*** Error: %s -> %s: %s" % (ex, pt.id, case_id)
        