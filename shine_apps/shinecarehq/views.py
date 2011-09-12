from couchdbkit.exceptions import ResourceNotFound
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from casexml.apps.case.models import CommCareCase
from patient.models.patientmodels import BasePatient, Patient

#
#class MepiPatientListView(PatientListView):
#    def get_context_data(self, **kwargs):
#        request = self.request
#        context = super(MepiPatientListView, self).get_context_data(**kwargs)
#        #cases = CommCareCase.view("shinepatient/shine_patient_cases", include_docs=True).all()
#        #making big assumption that it's 1:1 for patient->case at this juncture
#        return context
#    pass
from shinepatient.models import ShinePatient

@login_required()
def my_cases(request, template="shinecarehq/my_cases.html"):
    return render_to_response(template,
                              {},
                              context_instance=RequestContext(request)
    )

@login_required()
def case_dashboard(request, template="shinecarehq/patient_dashboard.html"):
    """
    Full case list for dashboard view
    """

    patients = ShinePatient.view("shinepatient/shine_patients", include_docs=True).all()
    return render_to_response(template, {"patients": patients}, context_instance=RequestContext(request))

@login_required()
def all_cases(request, template="shinecarehq/all_cases.html"):
    """
    Full case list
    """
    cases = CommCareCase.view("shinepatient/shine_patient_cases", include_docs=True).all()
    for case in cases:
        try:
            pat = BasePatient.get_typed_from_dict(BasePatient.get_db().get(case.patient_guid))
            case.patient_name = "%s %s" % (pat.first_name, pat.last_name)
        except ResourceNotFound:
            case.patient_name = None
    return render_to_response(template, {"cases": cases}, context_instance=RequestContext(request))


@login_required()
def latest_activity(request, template="shinecarehq/latest_activity.html"):
    return render_to_response(template,
                              {},
                              context_instance=RequestContext(request)
    )

@login_required()
def view_case(request, case_id, template="shinecarehq/mepi_case.html"):
    return render_to_response(template,
                                {},
                                context_instance=RequestContext(request)
    )

