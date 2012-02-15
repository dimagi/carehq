from carehqapp.models import CCDSubmission
from patient.models import Patient

def run():
    submits = CCDSubmission.view('carehqapp/ccd_submits_by_patient_doc', include_docs=True).all()

    for s in submits:
        try:
            #patient_guid = s.get_patient_guid()
            patient_guid = s._get_patient_guid_by_externalid()
            print patient_guid
            django_patient = Patient.objects.get(doc_id=patient_guid)

            CCDSubmission.check_and_generate_issue(s, django_patient, mutate_xform=False)
        except Exception, ex:
            print "Some error: %s" % ex
