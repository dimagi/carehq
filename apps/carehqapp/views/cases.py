from django.shortcuts import render_to_response
from django.template.context import RequestContext, RequestContext

def my_cases_patient(request, template_name = "carehqapp/my_cases_patient.html"):
    context = RequestContext(request)
    user = request.user
    context['user'] = user
    return render_to_response(template_name, context_instance=context)

def my_cases_caregiver(request, template_name = 'carehqapp/my_cases_caregiver.html'):
    context = RequestContext(request)
    user = request.user
    context['user'] = user
    return render_to_response(template_name, context_instance=context)

def my_case_provider(request, template_name = 'carehqapp/my_cases_provider.html'):
    context = RequestContext(request)
    user = request.user
    context['user'] = user
    return render_to_response(template_name, context_instance=context)

def cases_patient(request, patient_id, template_name='carehqapp/cases_patient.html'):
    context = RequestContext(request)
    user = request.user
    context['user'] = user
    return render_to_response(template_name, context_instance=context)





