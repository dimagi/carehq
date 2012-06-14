from xml.etree import ElementTree
import isodate
import simplejson
from casexml.apps.case.models import CommCareCase
from casexml.apps.case.signals import process_cases
from casexml.apps.case.tests.util import CaseBlock
from couchforms.util import post_xform_to_couch
from dimagi.utils.make_time import make_time
from pactpatient.models import PactPatient
from patient.models import Patient
from django.contrib.auth.models import User

def process_dots_json(doc, dots_json):
    username = doc['form']['Meta']['username']
    user = User.objects.get(username=username)
    #kinda nasty but get the pact_id for patient lookup
    patient_doc = PactPatient.view('pactcarehq/patient_pact_ids', key=doc['form']['pact_id']).first()
    pt = Patient.objects.get(doc_id=patient_doc._id)
    return Observation.from_json(dots_json, pt, user, doc) #provider=provider_actor, patient=pt, json=dots_json)


def recompute_dots_casedata(patient_doc):
    #reconcile and resubmit DOT json - commcare2.0
    dots_data = patient_doc.get_dots_data()
    case = CommCareCase.get(patient_doc.case_id)
    if case.opened_on is None:
        #hack calculate the opened on date from the first xform
        opened_date = case.actions[0].date
    else:
        opened_date = case.opened_on

    owner_id = case.owner_id
    update_dict = {'dots': simplejson.dumps(dots_data)}

    caseblock = CaseBlock(case._id, update=update_dict, owner_id=owner_id, external_id=patient_doc.pact_id, case_type='', date_opened=opened_date, close=False, date_modified=make_time().strftime("%Y-%m-%dT%H:%M:%SZ"))
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
    process_cases(sender="dotsupdate", xform=xform_posted)