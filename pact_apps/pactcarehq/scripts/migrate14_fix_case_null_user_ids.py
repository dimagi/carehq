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



def run():
    #convert patient from pact_id 493 to 199 due to a clerical/data entry accounting error. This should not be done
    #in other circumstances.

    from casexml.apps.case.models import CommCareCase


    patients = Patient.objects.all()
    for pt in patients:
        print "Patient: %s" % pt.couchdoc._id
        patient_doc = pt.couchdoc
        case_id = pt.couchdoc.case_id

#
#        #todo, make this a case update
        casedoc = CommCareCase.get(case_id)
        if casedoc.user_id is None:
            print "Updating CaseID: %s" % case_id
            casedoc.user_id = ''
            casedoc.save()







