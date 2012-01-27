from couchdbkit.exceptions import ResourceNotFound
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from casexml.apps.case.models import CommCareCase
from pactpatient.updater import update_patient_casexml
from patient.models import Patient
import sys
import traceback
import re
from receiver.util import spoof_submission

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


def get_case_phone(num, case):
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

def get_case_address(num, case):
    ret = {}

    if hasattr(case, 'address%d' % num):
        ret['address'] = getattr(case, 'address%d' % num)
    else:
        return {}

    if hasattr(case, 'address%dtype' % num):
        ret['description'] = getattr(case, 'address%dtype' % num)
    else:
        ret['description'] = None
    return ret

def cmp_phone(phone1, phone2):
    p1 = phone1.replace('-','').replace('(', '').replace(')','').replace(' ','')
    p2 = phone2.replace('-','').replace('(', '').replace(')','').replace(' ','')
    return p1==p2

def cmp_addr(caddr, case_addr):
    old_addr = '%s%s%s%s' % (caddr.street, caddr.city, caddr.state, caddr.postal_code)

    old_addr_cmp = old_addr.lower().replace(',','').replace(' ','').replace('.','').replace('-','')
    case_addr_cmp = case_addr.lower().replace(',','').replace(' ','').replace('.','').replace('-','')
    return old_addr_cmp == case_addr_cmp

def run():

#    print "this migration has been run in production sunday aug 21 2011 at 1:16 am est"
#    return
    patients = Patient.objects.all()
    for pt in patients:
        try:
            print "\t###Patient %s" % pt.id
            cpatient = pt.couchdoc
            case_id = cpatient.case_id
            try:
                case = CommCareCase.get(case_id)
            except:
                case = None

            if case is not None:
                prop_keys = case._dynamic_properties.keys()
                addr_keys = filter(filter_addr_phone, prop_keys)
                addr_keys.sort()
                merged_phones = pt.couchdoc.casexml_phones()

                merged_addrs = pt.couchdoc.casexml_addresses
            else:

                merged_phones = []
                merged_addrs = []


            #############################################
            #compare phones
            for i, p in enumerate(cpatient.phones):
                if p.number != '' and p.deprecated == False:
                    #print "\t  ### Phone %d ####" % (i)
                    #print "\t\tCPatient Phone: %s: %s (%s)" % (p.description, p.number, p.deprecated)
                    pass
                else:
                    continue
                matched_phone=False
                for q in range(1,5):
                    phone_dict = get_case_phone(q, case)

                    if len(phone_dict.keys()) > 0:
                        #print "\t\tCase phone: %s: %s" % (phone_dict['description'], phone_dict['number'])
                        if cmp_phone(p.number,phone_dict['number']):
                            #phone matches
                            #print "\t\t\tMatches with casexml! %s" % (phone_dict['number'])
                            matched_phone=True

                if matched_phone==False:
                    #print "\t\tUnmatched phone in couchdoc, set to case!"
                    merged_phones.append({'number':p.number, 'description':p.description})


            #############################################
            #compare addresses
            for i, addr in enumerate(cpatient.address):
                if addr.street != '' and addr.city != '' and addr.deprecated == False:
                    print "\t  ### Address %d ####" % (i)
                    print "\t\tCPatient Address: %s: %s (%s)" % (addr.description, addr.get_full_address(), addr.deprecated)
                else:
                    continue
                matched_addr=False
                for q in range(1,5):
                    addr_dict = get_case_address(q, case)

                    if len(addr_dict.keys()) > 0:
                        if cmp_addr(addr,addr_dict['address']):
                            #address matches
                            print "\t\t\tMatches with casexml! %s" % (addr_dict['address'])
                            matched_addr=True

                if matched_addr == False:
                    #print "\t\tUnmatched address in couchdoc, set to case!"
                    merged_addrs.append({"address": "%s %s, %s %s" % (addr.street, addr.city, addr.state, addr.postal_code), 'description': addr.description})
                    #print "\t\t\tFinished append: %s %s, %s %s" % (addr.street, addr.city, addr.state, addr.postal_code)

            xml_body = update_patient_casexml(User.objects.all().filter(username='admin')[0], pt.couchdoc.case_id, pt.couchdoc.pact_id, merged_phones, merged_addrs)
            spoof_submission(reverse("receiver.views.post"), xml_body, hqsubmission=False)
            #todo: deprecate addrs and phones!


        except ResourceNotFound, ex:
            print "\t\tNot present"
        except Exception, ex:
            print traceback.print_tb(sys.exc_info()[2])
            print ex.message
            print ex.__class__
            print "\t\t*** Error: %s -> %s: %s" % (ex, pt.id, case_id)
        