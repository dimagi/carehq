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
from patient.models import Patient

def run():
    #convert patient from pact_id 493 to 199 due to a clerical/data entry accounting error. This should not be done
    #in other circumstances.

    from casexml.apps.case.models import CommCareCase


    patients = Patient.objects.all()
    for pt in patients:
        patient_doc = pt.couchdoc
        case_id = pt.couchdoc.case_id
        print case_id
        casedoc = CommCareCase.get(case_id)

        update_dict = patient_doc.calculate_regimen_caseblock()
        caseblock = CaseBlock(case_id, update=update_dict, owner_id='', external_id=patient_doc.pact_id, case_type='', date_opened=casedoc.actions[0]['date'], date_modified=casedoc.actions[0]['date']) #make_time())
        print update_dict
        continue

        def isodate_string(date):
            if date: return isodate.datetime_isoformat(date) + "Z"
            return ""

        case_blocks = [caseblock.as_xml(format_datetime=isodate_string)]

        form = ElementTree.Element("data")
        form.attrib['xmlns'] = "https://www.commcarehq.org/test/casexml-wrapper"
        form.attrib['xmlns:jrm'] ="http://openrosa.org/jr/xforms"
        for block in case_blocks:
            form.append(block)
        xform = ElementTree.tostring(form)
        print xform
        xform_posted = post_xform_to_couch(ElementTree.tostring(form))
        process_cases(sender="pactapi", xform=xform_posted)

        casedoc2 = CommCareCase.get(case_id)






