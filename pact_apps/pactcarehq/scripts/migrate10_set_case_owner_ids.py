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
from pactcarehq.fixturegenerators import PACT_HP_GROUP_ID
from patient.models import Patient

def compute_case_info(patient_doc):
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

    case_id = patient_doc.case_id
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

#    update_dict = {
#        'owner_id': owner_id,
#        'user_id': str(user_id),
#        'case_name': case_name,
#        'case_type': case_type,
#        }

    #print update_dict
    caseblock = CaseBlock(case._id, owner_id=owner_id, external_id=patient_doc.pact_id, create=True, case_type=case_type,case_name=case_name, user_id=str(user_id), date_opened=opened_date, close=False, date_modified=make_time().strftime("%Y-%m-%dT%H:%M:%SZ"))
    #'2011-08-24T07:42:49.473-07') #make_time())

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
    print xform
    xform_posted = post_xform_to_couch(ElementTree.tostring(form))
    process_cases(sender="computecasedata", xform=xform_posted)


def run():
    #convert patient from pact_id 493 to 199 due to a clerical/data entry accounting error. This should not be done
    #in other circumstances.

    from casexml.apps.case.models import CommCareCase


    patients = Patient.objects.all()
    for pt in patients:
        print "Patient: %s" % pt.couchdoc._id
        patient_doc = pt.couchdoc

        case_id = pt.couchdoc.case_id

        print "Updating CaseID: %s" % case_id
#        print owner_username
#        print user_id
#
#        #todo, make this a case update
        #casedoc = CommCareCase.get(case_id)
#        casedoc.owner_id = str(user_id)
        #casedoc.user_id = str(user_id)
#        casedoc.case_name = case_name
#        casedoc.case_type = case_type
        #casedoc.save()

        compute_case_info(pt.couchdoc)







