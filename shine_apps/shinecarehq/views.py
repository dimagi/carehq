from couchdbkit.exceptions import ResourceNotFound
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from casexml.apps.case.models import CommCareCase
from couchforms.models import XFormInstance
from patient.models.patientmodels import BasePatient, Patient
from datetime import datetime, timedelta

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
def emergency_lab_dashboard(request, template="shinecarehq/emergency_lab_dashboard.html"):
    patients = ShinePatient.view("shinepatient/shine_patients", include_docs=True).all()
    return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required()
def labs_dashboard(request, template="shinecarehq/labs_dashboard.html"):
    """
    Full case list for dashboard view
    """
    patients = ShinePatient.view("shinepatient/shine_patients", include_docs=True).all()
    return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required()
def hiv_dashboard(request, template="shinecarehq/hiv_dashboard.html"):
    """
    Full case list for dashboard view
    """
    patients = ShinePatient.view("shinepatient/shine_patients", include_docs=True).all()
    return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required()
def clinical_dashboard(request, template="shinecarehq/clinical_dashboard.html"):
    """
    Full case list for dashboard view
    """

    patients = ShinePatient.view("shinepatient/shine_patients", include_docs=True).all()
    return render_to_response(template, locals(), context_instance=RequestContext(request))


@login_required()
def recent_activity(request, template="shinecarehq/recent_activity.html"):
    day_range = int(request.GET.get('range', 7))
    startkey = (datetime.utcnow() - timedelta(days=day_range)).strftime('%Y-%m-%d')
    endkey = datetime.utcnow().strftime('%Y-%m-%d')

    activities = XFormInstance.view('shinecarehq/all_submits_by_date', startkey=startkey, endkey=endkey, include_docs=True, reverse=True).all()
    return render_to_response(template, {'submissions': activities}, context_instance=RequestContext(request))




@login_required()
def case_dashboard(request, template="shinecarehq/patient_dashboard.html"):
    """
    Full case list for dashboard view
    """

    show_param = request.GET.get('show', 'all')

    patients = ShinePatient.view("shinepatient/shine_patients", include_docs=True).all()

    for pt in patients:
        pt.cache_clinical_case()

    active= filter(lambda x: not x.latest_case.closed, patients)
    inactive = set.difference(set(patients), set(active))
    enrolled_today = filter(lambda x: x.get_last_action[1] == 'Enrollment' and x.get_last_action[0].date() == datetime.utcnow().date(), patients)
    only_enrolled = filter(lambda x: x.get_last_action[1] == 'Enrollment', patients)
    positive = filter(lambda x: x.get_culture_status == 'positive', patients)
    negative = filter(lambda x: x.get_culture_status == 'negative', patients)
    contaminated = filter(lambda x: x.latest_case.dynamic_properties().get('contamination', '') == 'yes', patients)


    if show_param == 'all':
        show_list = patients
        show_string = "All Patients"
    elif show_param == 'active':
        show_list = active
        show_string = "Active Patients"
    elif show_param == 'inactive':
        show_list = inactive
        show_string = 'Inactive Patients'
    elif show_param=='enrolled_today':
        show_string="Patients Enrolled Today"
        show_list = enrolled_today
    elif show_param == 'needing_fup':
        show_string="Patients Needing Follow Up"
        show_list = only_enrolled
    elif show_param == 'positive':
        show_string = "Positive Blood Cultures"
        show_list = positive
    elif show_param == 'negative':
        show_string = "Negative Blood Cultures"
        show_list = negative
    elif show_param == 'contaminated':
        show_string = "Contaminated Blood Cultures"
        show_list = contaminated



    return render_to_response(template, locals(), context_instance=RequestContext(request))

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

@login_required
def show_submission(request, doc_id, template_name="shinecarehq/view_mepi_submission.html"):
    context = RequestContext(request)
    xform = XFormInstance.get(doc_id)
    form_data = xform['form']
    #context['form_type'] = form_xmlns_to_names.get(xform.xmlns, "Unknown")
    context['form_type'] = xform.xmlns
    context['xform'] = xform
    return render_to_response(template_name, context_instance=context)
