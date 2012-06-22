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
from pactpatient import caseapi
from pactpatient.models import html_escape
from patient.models import Patient

def compute_case_update(patient_doc):
    """
    One time use of this function, hence why it's duped functionality
    """
    #reconcile and resubmit DOT json - commcare2.0
    case = CommCareCase.get(patient_doc.case_id)

    dot_status = case.dot_status

    if dot_status != '':
        print "Setting Schedule: %s" % patient_doc._id
        x = caseapi.compute_schedule_block(patient_doc)
        print x._id

def run():
    #convert patient from pact_id 493 to 199 due to a clerical/data entry accounting error. This should not be done
    #in other circumstances.
    patients = Patient.objects.all()
    for pt in patients:
        print "Patient: %s" % pt.couchdoc._id
        compute_case_update(pt.couchdoc)







