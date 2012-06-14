from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from xml.etree import ElementTree
import isodate
from auditcare.models import AuditEvent
from casexml.apps.case.models import CommCareCase
from casexml.apps.case.signals import process_cases
from casexml.apps.case.tests.util import CaseBlock
from couchforms.util import post_xform_to_couch
from couchlog.models import ExceptionRecord
from dimagi.utils.make_time import make_time
from dotsview.formprocess import recompute_dots_casedata
from pactpatient.forms.patient_form import PactPatientForm
from patient.models import Patient
from django.test.client import Client

def run():

    """
    Loop through all the regimens for patients and spoof submit the old regimens to new (default) labeled ones and update the caseblock accordingly
    """
    client = Client()
    from casexml.apps.case.models import CommCareCase
    patients = Patient.objects.all()
    for pt in patients:
        patient_doc = pt.couchdoc
        print "recomputing patient dot: %s" % patient_doc._id

        if patient_doc.is_dot_patient():
            print "\tRecomputing"
            recompute_dots_casedata(patient_doc)
        else:
            print "\tNot a DOT patient, skipping"





