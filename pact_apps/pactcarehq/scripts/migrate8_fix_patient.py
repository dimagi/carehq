from casexml.apps.case.models import CommCareCase
from patient.models import Patient

def run():
    #convert patient from pact_id 493 to 199 due to a clerical/data entry accounting error. This should not be done
    #in other circumstances.

    from couchforms.models import XFormInstance
    db = XFormInstance.get_db()
    xforms = XFormInstance.view('pactcarehq/all_submits_by_patient_date', startkey=['493',0], endkey=['493',9999], include_docs=True).all()

    for x in xforms:
        x['form']['pact_id'] = '199'
        x.save()
        print "flipping form's pact_id from 493->199"


    django_patient = Patient.objects.get(doc_id='822b449e99f54c978097d21b14575cb3') #493
    patient_doc = django_patient.couchdoc
    if patient_doc.pact_id =='493':
        print "flipping patient 493->199"
        patient_doc.pact_id='199'
        patient_doc.save()

    case_id = patient_doc.case_id

    case = CommCareCase.get(case_id)
    if case.external_id == '493':
        case.external_id = '199'
        case.save()
        print "flipping case 493->199"


