from casexml.apps.case.models import CommCareCase
from couchforms.models import XFormInstance
from shinepatient.models import ShinePatient
from shinepatient.signals import process_shinepatient_registration

def run():
    """
    Try to retrigger signal on xforms that don't have appropriate patients configured for them
    """

    registrations = XFormInstance.view('couchforms/by_xmlns', key='http://shine.commcarehq.org/patient/reg', reduce=False, include_docs=True).all()
    for submit in registrations:
        #query the shinepatient/patient_cases_all and see if the case id exists.
        case_id = submit['form']['case']['case_id']
        pts = ShinePatient.view('shinepatient/patient_cases_all', key=case_id, include_docs=True).all()
        if len(pts) == 0:
            print "patient not registered! %s" % submit._id
            process_shinepatient_registration(None, submit)
#            try:
#                case = CommCareCase.get(case_id)
#                print "Case found: %s" % case_id
#            except:
#                print "No case found: %s" % case_id

