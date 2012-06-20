from xml.etree import ElementTree
from django.contrib.auth.models import User
import isodate
import simplejson
from auditcare.models import AuditEvent
from casexml.apps.case.models import CommCareCase
from casexml.apps.case.signals import process_cases
from casexml.apps.case.tests.util import CaseBlock
from couchforms.util import post_xform_to_couch
from couchlog.models import ExceptionRecord
from dimagi.utils.make_time import make_time
from pactpatient.models import html_escape
from patient.models import Patient



pactid_hpstatus_map = {
    '62': 1,
    '65': 1,
    '96': 1,
    '97': 2,
    '114': 2,
    '122': 1,
    '153': 1,
    '164': 1,
    '171': 1,
    '173': 1,
    '179': 1,
    '195': 2,
    '198': 1,
    '199': 3,
    '208': 1,
    '227': 1,
    '234': 1,
    '237': 2,
    '256': 1,
    '279': 3,
    '282': 2,
    '286': 2,
    '294': 2,
    '306': 2,
    '324': 1,
    '327': 3,
    '332': 1,
    '338': 2,
    '348': 2,
    '349': 1,
    '361': 1,
    '366': 3,
    '370': 2,
    '401': 2,
    '404': 2,
    '406': 3,
    '409': 2,
    '412': 1,
    '415': 2,
    '418': 1,
    '419': 2,
    '421': 1,
    '422': 1,
    '424': 1,
    '427': 2,
    '431': 2,
    '432': 1,
    '433': 2,
    '436': 2,
    '438': 2,
    '442': 2,
    '451': 2,
    '452': 1,
    '454': 1,
    '459': 1,
    '462': 1,
    '467': 1,
    '468': 3,
    '474': 1,
    '476': 2,
    '477': 2,
    '478': 1,
    '479': 1,
    '481': 2,
    '483': 1,
    '486': 1,
    '487': 1,
    '489': 2,
    '490': 1,
    '492': 2,
    '494': 1,
    '495': 3,
    '496': 2,
    '497': 1,
    '498': 2,
    '499': 1,
    '500': 1,
    '501': 1,
    '502': 1,
    '504': 2,
    '505': 2,
    '507': 1,
    '509': 1,
    '510': 1,
    '511': 1,
    '512': 1,
    '513': 1,
    '514': 1,
    '515': 1,
    '516': 1,
    '517': 1,
    '518': 1,
    '166': 3,
    '403': 2,
    }

def compute_case_update(patient_doc):
    #reconcile and resubmit DOT json - commcare2.0
    case = CommCareCase.get(patient_doc.case_id)

    if case.arm.lower().startswith("dot"):
        dot_status = case.arm
    else:
        dot_status = ""

    pact_id = patient_doc.pact_id
    if pactid_hpstatus_map.has_key(pact_id):
        hp_status = "HP%d" % pactid_hpstatus_map[pact_id]
    else:
        hp_status="HP1"
        print " # Not Found: %s, arm: %s" % (pact_id, case.arm)

    if case.opened_on is None:
        #hack calculate the opened on date from the first xform
        opened_date = case.actions[0].date
    else:
        opened_date = case.opened_on

    case_id = patient_doc.case_id
    owner_id = case.owner_id

    owner_id = case.owner_id
    if owner_id is None:
        owner_id = ''

    update_dict = {
        'dot_status': dot_status,
        'arm': patient_doc.arm, #arm
        'hp_status': hp_status,
        }

    #print update_dict
    print update_dict
    caseblock = CaseBlock(case._id, owner_id=owner_id, external_id=patient_doc.pact_id, update=update_dict, date_opened=opened_date, close=False, date_modified=make_time().strftime("%Y-%m-%dT%H:%M:%SZ"))

    def isodate_string(date):
        if date: return isodate.datetime_isoformat(date) + "Z"
        return ""

    case_blocks = [caseblock.as_xml(format_datetime=isodate_string)]

    form = ElementTree.Element("data")
    form.attrib['xmlns'] = "http://dev.commcarehq.org/pact/patientupdate"
    form.attrib['xmlns:jrm'] ="http://openrosa.org/jr/xforms"
    for block in case_blocks:
        form.append(block)
    xform = ElementTree.tostring(form)
    xform_posted = post_xform_to_couch(ElementTree.tostring(form))
    process_cases(sender="computecasedata", xform=xform_posted)

def run():
    #convert patient from pact_id 493 to 199 due to a clerical/data entry accounting error. This should not be done
    #in other circumstances.
    patients = Patient.objects.all()
    for pt in patients:
        print "Patient: %s" % pt.couchdoc._id
        compute_case_update(pt.couchdoc)







