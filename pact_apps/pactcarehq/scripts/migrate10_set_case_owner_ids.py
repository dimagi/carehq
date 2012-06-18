from django.contrib.auth.models import User
from auditcare.models import AuditEvent
from casexml.apps.case.models import CommCareCase
from couchlog.models import ExceptionRecord
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
        owner_username = patient_doc.primary_hp
        try:
            user_id = User.objects.get(username=owner_username).id
        except:
            print "\tno userid, continuing: #%s#" % owner_username
            user_id = ""
            continue

        print "CaseID: %s" % case_id
        print owner_username
        print user_id

        #todo, make this a case update
        casedoc = CommCareCase.get(case_id)
        casedoc.owner_id = str(user_id)
        casedoc.user_id = str(user_id)
        casedoc.save()







