from pactpatient import caseapi
from patient.models import Patient
from django.test.client import Client

def run():

    """
    Loop through all the regimens for patients and spoof submit the old regimens to new (default) labeled ones and update the caseblock accordingly
    """
    client = Client()
    patients = Patient.objects.all()
    for pt in patients:
        patient_doc = pt.couchdoc
        print "recomputing patient dot: %s" % patient_doc._id

        if patient_doc.is_dot_patient():
            print "\tRecomputing"
            caseapi.recompute_dots_casedata(patient_doc)
        else:
            print "\tNot a DOT patient, skipping"





