from xml.etree import ElementTree
from django.contrib.auth.models import User
import isodate
import simplejson
from casexml.apps.case.models import CommCareCase
from casexml.apps.case.signals import process_cases
from casexml.apps.case.tests.util import CaseBlock
from casexml.apps.case.xml import V2
from couchforms.util import post_xform_to_couch
from dimagi.utils.make_time import make_time
from dimagi.utils.printing import print_pretty_xml
from pactcarehq.fixturegenerators import PACT_HP_GROUP_ID
from pactpatient.models import html_escape

def isodate_string(date):
    if date: return isodate.datetime_isoformat(date) + "Z"
    return ""


def getform():
    form = ElementTree.Element("data")
    form.attrib['xmlns'] = "http://dev.commcarehq.org/pact/patientupdate"
    form.attrib['xmlns:jrm'] = "http://openrosa.org/jr/xforms"
    return form


def compute_case_create_block(patient_doc):
    #reconcile and resubmit DOT json - commcare2.0
    dots_data = patient_doc.get_dots_data()
    case = CommCareCase.get(patient_doc.case_id)
    del(case.type)
    case.save()

    if case.opened_on is None:
        #hack calculate the opened on date from the first xform
        opened_date = case.actions[0].date
    else:
        opened_date = case.opened_on

    owner_username = patient_doc.primary_hp
    try:
        user_id = User.objects.get(username=owner_username).id
    except:
        print "\tno userid, setting blank for #%s#" % owner_username
        user_id = ""

    if user_id is None:
        user_id = ''

    case_name = "%s %s" % (patient_doc.first_name, patient_doc.last_name)
    case_type = "cc_path_client"

    owner_id = PACT_HP_GROUP_ID
    caseblock = CaseBlock(case._id, owner_id=owner_id, external_id=patient_doc.pact_id, create=True, case_type=case_type
        , case_name=case_name, user_id=str(user_id), date_opened=opened_date, close=False,
        date_modified=make_time().strftime("%Y-%m-%dT%H:%M:%SZ"), version=V2)
    case_blocks = [caseblock.as_xml(format_datetime=isodate_string)]
    return submit_blocks(case_blocks, "compute_pactpatient_create_block")


def recompute_dots_casedata(patient_doc):
    """
    Recompute and reset the ART regimen and NONART regimen to whatever the server says it is, in the case where there's an idiosyncracy with how the phone has it set.
    """
    #reconcile and resubmit DOT json - commcare2.0
    case = CommCareCase.get(patient_doc.case_id)
    if case.opened_on is None:
        #hack calculate the opened on date from the first xform
        opened_date = case.actions[0].date
    else:
        opened_date = case.opened_on

    owner_id = case.owner_id
    update_dict = patient_doc.calculate_regimen_caseblock()
    update_dict['pactid'] =  patient_doc.pact_id

    dots_data = patient_doc.get_dots_data()
    update_dict['dots'] =  simplejson.dumps(dots_data)

    caseblock = CaseBlock(case._id, update=update_dict, owner_id=owner_id, external_id=patient_doc.pact_id, case_type='cc_path_client', date_opened=opened_date, close=False, date_modified=make_time().strftime("%Y-%m-%dT%H:%M:%SZ"), version=V2)
    #'2011-08-24T07:42:49.473-07') #make_time())

    case_blocks = [caseblock.as_xml(format_datetime=isodate_string)]
    return submit_blocks(case_blocks, "compute_pactpatient_dots")



def phone_addr_updater(patient_doc, active_phones, active_addresses):
    """
    active_phones = [{'phone':'', 'description': ''}, ...]
    active_addresses = [{'address':'', 'description': ''}, ...]
    """
    #reconcile and resubmit DOT json - commcare2.0
    #patient_doc.save()
    case = CommCareCase.get(patient_doc.case_id)
    if case.opened_on is None:
        #hack calculate the opened on date from the first xform
        opened_date = case.actions[0].date
    else:
        opened_date = case.opened_on
    owner_username = patient_doc.primary_hp
    try:
        user_id = User.objects.get(username=owner_username).id
    except:
        print "\tno userid, setting blank for #%s#" % owner_username
        user_id = ""

    if user_id is None:
        user_id = ''

    owner_id = case.owner_id
    if owner_id is None:
        owner_id = ''

    update_dict = {
        'pactid': patient_doc.pact_id,
        }


    filtered_phones = filter(lambda x: len(x['number']) > 0 and len(x['description']) >= 0, active_phones)
    #for i, p in enumerate(active_phones, start=1):
    for i in range(0,5):
        if i < len(filtered_phones):
            p = filtered_phones[i]
        else:
            p = {'number':'', 'description':''}
        #phone_xml.append(get_phone_xml(i+1, p['number'], typestring=p['description']))
        update_dict['Phone%dType' % (i+1)] = p['description']
        update_dict['Phone%d' % (i+1)] = p['number']

    filtered_addresses = filter(lambda x: len(x['address']) > 0 and len(x['description']) >= 0, active_addresses)
    #for i, a in enumerate(active_addresses, start=1):
    for i in range(0,5):
        if i < len(filtered_addresses):
            a = filtered_addresses[i]
        else:
            a = {'address': '', 'description': ''}
        update_dict['address%dtype' % (i+1)] = a['description']
        update_dict['address%d' % (i+1)] = a['address']

    caseblock = CaseBlock(case._id, owner_id=owner_id, external_id=patient_doc.pact_id, update=update_dict,
        user_id=str(user_id), date_opened=opened_date, close=False,
        date_modified=make_time().strftime("%Y-%m-%dT%H:%M:%SZ"), version=V2)

    case_blocks = [caseblock.as_xml(format_datetime=isodate_string)]
    return submit_blocks(case_blocks, "compute_pactpatient_update_phone_addr")

def compute_case_update_block(patient_doc, include_dots=False, close=False):
    #reconcile and resubmit DOT json - commcare2.0
    #patient_doc.save()
    case = CommCareCase.get(patient_doc.case_id)
    if case.opened_on is None:
        #hack calculate the opened on date from the first xform
        opened_date = case.actions[0].date
    else:
        opened_date = case.opened_on
    owner_username = patient_doc.primary_hp
    try:
        user_id = User.objects.get(username=owner_username).id
    except:
        print "\tno userid, setting blank for #%s#" % owner_username
        user_id = ""

    if user_id is None:
        user_id = ''

    owner_id = case.owner_id
    if owner_id is None:
        owner_id = ''

    update_dict = {
        'initials': "%s%s" % (patient_doc.first_name[0], patient_doc.last_name[0]),
        'pactid': patient_doc.pact_id,
        'gender': patient_doc.gender,
        'dob': patient_doc.birthdate.strftime("%Y-%m-%d"),
        'hp': patient_doc.primary_hp,
        'patient_notes': html_escape(patient_doc.notes) if patient_doc.notes != None else "",
        'dot_status': patient_doc.dot_status,
        'hp_status': patient_doc.hp_status,
        }

    if include_dots:
        update_dict.update(patient_doc.calculate_regimen_caseblock())
        dots_data = patient_doc.get_dots_data()
        update_dict['dots'] =  simplejson.dumps(dots_data)

    caseblock = CaseBlock(case._id, owner_id=owner_id, external_id=patient_doc.pact_id, update=update_dict,
        user_id=str(user_id), date_opened=opened_date, close=False,
        date_modified=make_time().strftime("%Y-%m-%dT%H:%M:%SZ"), version=V2)
    case_blocks = [caseblock.as_xml(format_datetime=isodate_string)]
    return submit_blocks(case_blocks, "compute_pactpatient_update_general")

def compute_schedule_block(patient_doc):
    #reconcile and resubmit DOT json - commcare2.0
    #patient_doc.save()
    case = CommCareCase.get(patient_doc.case_id)
    if case.opened_on is None:
        #hack calculate the opened on date from the first xform
        opened_date = case.actions[0].date
    else:
        opened_date = case.opened_on
    owner_username = patient_doc.primary_hp
    try:
        user_id = User.objects.get(username=owner_username).id
    except:
        print "\tno userid, setting blank for #%s#" % owner_username
        user_id = ""

    if user_id is None:
        user_id = ''

    owner_id = case.owner_id
    if owner_id is None:
        owner_id = ''

    update_dict = patient_doc.get_latest_schedule()

    caseblock = CaseBlock(case._id, owner_id=owner_id, external_id=patient_doc.pact_id, update=update_dict,
        user_id=str(user_id), date_opened=opened_date, close=False,
        date_modified=make_time().strftime("%Y-%m-%dT%H:%M:%SZ"), version=V2)
    case_blocks = [caseblock.as_xml(format_datetime=isodate_string)]
    return submit_blocks(case_blocks, "compute_pactpatient_update_general")


def submit_blocks(case_blocks, sender_name):
    form = ElementTree.Element("data")
    form.attrib['xmlns'] = "http://dev.commcarehq.org/pact/patientupdate"
    form.attrib['xmlns:jrm'] = "http://openrosa.org/jr/xforms"
    for block in case_blocks:
        form.append(block)
    submission_xml_string = ElementTree.tostring(form)
    print "#################################\nCase Update Submission: %s" % sender_name
    print_pretty_xml(submission_xml_string)
    print "#################################\n\n"
    xform_posted = post_xform_to_couch(ElementTree.tostring(form))
    process_cases(sender=sender_name, xform=xform_posted)
    return xform_posted