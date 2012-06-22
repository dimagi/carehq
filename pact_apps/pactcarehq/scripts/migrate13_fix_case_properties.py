from patient.models import Patient




def run():
    #convert patient from pact_id 493 to 199 due to a clerical/data entry accounting error. This should not be done
    #in other circumstances.
    patients = Patient.objects.all()
    for pt in patients:
        print "Patient: %s" % pt.couchdoc._id
        patient_doc = pt.couchdoc
        case_id = pt.couchdoc.case_id
        print "Updating CaseID: %s" % case_id
        caseapi.compute_case_update_block(pt.couchdoc)







