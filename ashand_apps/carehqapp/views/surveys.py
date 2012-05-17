from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from carehqapp.forms.survey_form import SurveyForm
from patient.models import BasePatient

@login_required
def caregiver_midpoint(request, patient_guid):
    return survey_view(request, patient_guid, 'caregiver_midpoint')


@login_required
def caregiver_endpoint(request, patient_guid):
    return survey_view(request, patient_guid, 'caregiver_endpoint')

@login_required
def patient_endpoint(request, patient_guid):
    return survey_view(request, patient_guid, 'patient_endpoint')



def survey_view(request, patient_guid, mode):
    context = RequestContext(request)
    patient_doc = BasePatient.get_typed_from_dict(BasePatient.get_db().get(patient_guid))

    user = request.user
    if mode == "caregiver_midpoint":
        context['survey_title'] = "Caregiver Midpoint Assessment"
        context['survey_preamble'] = "For caregivers in the ASHand system, this is survey 1 of 2 you will be doing for this study.  This should be done at week 2 of your patient's 4 week usage of the home monitoring system."
    if mode == "caregiver_endpoint":
        context['survey_title'] = "Caregiver Endpoint Assessment"
        context['survey_preamble'] = "For caregivers in the ASHand system, this is survey 2 of 2 you will be doing for this study.  This should be done at the conclusion of the study."
    if mode == "patient_endpoint":
        context['survey_title'] = "Patient Endpoint Assessment"
        context['survey_preamble'] = "For patients in the ASHand study.  At the study's end, please take the chance to view the data you generated on the system in ASHand.  This will either involve a direct login to the system, a phone guided tour of it, or you viewing your information on your caregiver's computer.  The responses here should be with regard to what you see on the web"
    context['form'] = SurveyForm(initial={'patient_doc_id': patient_guid, 'survey_context': mode, 'user': user.username})
    if request.method == "POST":
        form = SurveyForm(data=request.POST)
        if form.is_valid():
            survey = form.save(commit=False)

            if not hasattr(patient_doc, 'surveys'):
                patient_doc.surveys = {}
            patient_doc.surveys[mode] = survey.to_json()
            patient_doc.save()
            return HttpResponseRedirect(reverse('patient_url', kwargs={'patient_guid': patient_guid, 'view_mode': 'surveys'}))
        else:
            context['form'] = form


    template = "carehqapp/usability_survey.html"
    return render_to_response(template, context_instance=context)


