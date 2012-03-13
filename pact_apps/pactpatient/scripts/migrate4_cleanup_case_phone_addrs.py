import uuid
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from casexml.apps.case.models import CommCareCase
from pactpatient.models import PactPatient
from pactpatient.updater import update_patient_casexml
from receiver.util import spoof_submission


def cleanup_phones(case):
    phone_props = sorted(filter(lambda x: x.startswith("Phone"), case._dynamic_properties.keys()))
    reset_phones = []
    for n in range(0,6):
        phone_prop = 'Phone%d' % n
        type_prop = 'Phone%dType' % n
        if phone_prop in phone_props:
            phone = getattr(case,phone_prop,None)
        else:
            phone=None

        if type_prop in phone_props:
            phone_type = getattr(case, type_prop,None)
        else:
            phone_type = None


        if phone_type is None:
            continue
        if len(phone) == 0:
            continue

        to_add = {'number': phone, 'description': phone_type}
        if to_add not in reset_phones:
            reset_phones.append(to_add)
    #print reset_phones

    if len(reset_phones) > 4:
        print "phones too big!"
        print reset_phones
    return reset_phones

def cleanup_addrs(case):
    addr_props = sorted(filter(lambda x: x.startswith("address"), case._dynamic_properties.keys()))
    reset_addrs = []
    for n in range(0,6):
        addr_prop = 'address%d' % n
        type_prop = 'address%dtype' % n
        if addr_prop in addr_props:
            addr = getattr(case,addr_prop,None)
        else:
            addr=None

        if type_prop in addr_props:
            addr_type = getattr(case, type_prop,None)
        else:
            addr_type = None

        if addr_type is None:
            continue
        to_add = {'address': addr, 'description': addr_type}
        print to_add
        if to_add not in reset_addrs:
            reset_addrs.append(to_add)

    #print reset_addrs
    if len(reset_addrs) > 4:
        print "addrs too big!"
        print reset_addrs
    return reset_addrs


def do_reset_phone_addrs(case, pact_id=None):
    if pact_id is None:
        pact_id = uuid.uuid4().hex
    reset_phones = cleanup_phones(case)
    reset_addrs = cleanup_addrs(case)

    print reset_addrs

    #before submitting, remove the extraneous properties

    if hasattr(case, 'Phone5'):
        delattr(case,'Phone5')

    if hasattr(case, 'Phone5Type'):
        delattr(case,'Phone5Type')

    if hasattr(case, 'address5type'):
        delattr(case,'address5type')
    if hasattr(case, 'address5'):
        delattr(case,'address5')
    #case.save()
    xml_body = update_patient_casexml(User.objects.all().filter(username='admin')[0], case['_id'], pact_id, reset_phones, reset_addrs)
    #spoof_submission(reverse("receiver.views.post"), xml_body, hqsubmission=False)

def run():
    #really hacky script to address null issues in couch for patient data.  a weird issue not able to pinpoint.
    #patients = PactPatient.view('patient/all').all()
    ptdocs = PactPatient.view('patient/all', include_docs=True).all()
    for pt in ptdocs:
        if pt.case_id != '0bd56681dce2b7a5140f75266d20a9fb':
            continue
        print "#### Case-id: %s ####" % pt.case_id
        case = CommCareCase.get(pt['case_id'])
        do_reset_phone_addrs(case, pt.pact_id)

        #print xml_body
#
#
#
#
#
#
#        for p in phone_props:
#            propdict = {}
#            if p.endswith('Type'):
#                propdict['description'] = gettatr(case,p,'')
#            else:
#                propdict['number'] = getattr(case,p,'')
#            if len(propdict.keys()) == 2:
#                #check to see if it's viable
#
#
#            print "\t%s: #%s#" % (p, getattr(case, p, ''))



    #get_db().view('patient/all')
    #for pt in patients:
        #print pt
