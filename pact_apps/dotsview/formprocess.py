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

