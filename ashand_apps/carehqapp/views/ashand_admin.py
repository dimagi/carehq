from django.shortcuts import render_to_response
from django.template.context import RequestContext
from carehqapp.models import CCDSubmission
from patient.models import Patient

def admin_study_landing(request, template_name="carehqapp/admin_study_landing.html"):
    context = RequestContext(request)
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def admin_patient_list(request, template_name="carehqapp/admin_patient_list.html"):
    context = RequestContext(request)
    patients = Patient.objects.all()
    context['django_patients'] = patients
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def admin_provider_list(request, template_name="carehqapp/admin_provider_list.html"):
    pass

def admin_caregiver_list(request, template_name="carehqapp/admin_caregiver_list.html"):
    pass

def admin_ccd_submissions(request, template_name="carehqapp/admin_ccd_submissions.html"):
    context = RequestContext(request)
    submissions = CCDSubmission.view('carehqapp/ccd_submits_by_patient_doc', include_docs=True).all()
    context['submissions'] = submissions
    return render_to_response(template_name, context, context_instance=RequestContext(request))


def admin_user_activity(request, template_name="carehqapp/admin_user_activity.html"):
    context = RequestContext(request)
    submissions = []
    context['activities'] = submissions
    return render_to_response(template_name, context, context_instance=RequestContext(request))


