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
        case_id = pt.couchdoc.case_id
        print "Updating Case ID: %s" % case_id
        casedoc = CommCareCase.get(case_id)

        str_art = patient_doc.art_regimen
        str_non_art = patient_doc.non_art_regimen

        if str_art.lower() == 'qd':
            fix_art_regimen = 'morning'
        elif str_art.lower() == 'qd-am':
            fix_art_regimen = 'morning'
        elif str_art.lower() == 'qd-pm':
            fix_art_regimen = 'evening'
        elif str_art.lower() == 'bid':
            fix_art_regimen = 'morning,evening'
        elif str_art.lower() == 'qid':
            fix_art_regimen = 'morning,noon,evening,bedtime'
        elif str_art.lower() == 'tid':
            fix_art_regimen = 'morning,noon,evening'
        elif str_art.lower() == '' or str_art.lower() == 'none':
            fix_art_regimen = ''
        else:
            print "\tNo ART Change"
            fix_art_regimen=str_art.lower()

        if str_non_art.lower() == 'qd':
            fix_non_art_regimen = 'morning'
        elif str_non_art.lower() == 'qd-am':
            fix_non_art_regimen = 'morning'
        elif str_non_art.lower() == 'qd-pm':
            fix_non_art_regimen = 'evening'
        elif str_non_art.lower() == 'bid':
            fix_non_art_regimen = 'morning,evening'
        elif str_non_art.lower() == 'qid':
            fix_non_art_regimen = 'morning,noon,evening,bedtime'
        elif str_non_art.lower() == 'tid':
            fix_non_art_regimen = 'morning,noon,evening'
        elif str_non_art.lower() == '' or str_non_art.lower() == 'none':
            fix_non_art_regimen = ''
        else:
            print "\tNo Non ART Change"
            fix_non_art_regimen = str_non_art.lower()

        form = PactPatientForm('regimen', instance=patient_doc, data={'art_regimen': fix_art_regimen,'non_art_regimen':fix_non_art_regimen })
        print form.data
        response = client.post('/accounts/login/', {'username': 'mockmock@mockmock.com', 'password': 'mockmock'})
        response = client.post(reverse('ajax_post_patient_form', kwargs={'patient_guid':patient_doc._id, 'form_name':'ptedit'}), form.data )
        print response.status_code


