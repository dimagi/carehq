from casexml.apps.case.models import CommCareCase
from pactpatient.models.pactmodels import PactPatient
from patient.models.patientmodels import Patient

def run():
    django_pts = Patient.objects.all()
    heading = ['django_uuid', 'pt_doc_id', 'case_id', 'case_id_present']
    print ','.join(heading)
    for dp in django_pts:
        line = []
        line.append(dp.id)
        try:
            pact_doc = PactPatient.get(dp.doc_id)
            line.append(pact_doc._id)
        except:
            line.append('None')
            print ','.join(line)
            continue

        try:
            case_doc = CommCareCase.get(pact_doc.case_id)
            line.append(pact_doc.case_id)
            line.append("yes")
        except:
            case_doc = None
            line.append(pact_doc.case_id)
            line.append("no")

        print ','.join(line)

