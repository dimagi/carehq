from pactpatient import caseapi
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
#        print owner_username
#        print user_id
#
#        #todo, make this a case update
        #casedoc = CommCareCase.get(case_id)
#        casedoc.owner_id = str(user_id)
        #casedoc.user_id = str(user_id)
#        casedoc.case_name = case_name
#        casedoc.case_type = case_type
        #casedoc.save()

        caseapi.compute_case_create_block(pt.couchdoc)







