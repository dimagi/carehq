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

def run():
    #convert patient from pact_id 493 to 199 due to a clerical/data entry accounting error. This should not be done
    #in other circumstances.
    patients = Patient.objects.all()
    for pt in patients:
        patient_doc = pt.couchdoc
        if patient_doc is None:
            print "Patient doc none: %s" % pt.id
            continue
        case = CommCareCase.get(patient_doc.case_id)


        print "Patient: %s" % pt.couchdoc._id
        if case is not None:
            print "\thp_status: %s" % case.hp_status
            print "\tdot_status: %s" % case.dot_status
            patient_doc.hp_status = case.hp_status

            if case.dot_status != "" or case.dot_status != None:
                patient_doc.dot_status = case.dot_status
            patient_doc.save()


        else:
            print "\tNULL!"







