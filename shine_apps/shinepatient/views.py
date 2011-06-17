# To manage patient views for create/view/update you need to implement them directly in your patient app
from datetime import datetime
import logging
import urllib
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from patient.models import Patient
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from patient.models import BasePatient
from patient.forms import BasicPatientForm
from django.contrib import messages
from shinepatient.models import ShinePatient
from casexml.apps.case.models import CommCareCase
import json

@login_required
def new_patient(request):
    context = RequestContext(request)
    if request.method == 'POST':
        form = BasicPatientForm(data=request.POST)
        # make patient
        if form.is_valid():
            newptdoc = ShinePatient()
            newptdoc.patient_id = form.cleaned_data['patient_id']
            newptdoc.gender = form.cleaned_data['gender']
            newptdoc.birthdate = form.cleaned_data['birthdate']
            newptdoc.first_name = form.cleaned_data['first_name']
            newptdoc.last_name = form.cleaned_data['last_name']
            newptdoc.save()
            messages.add_message(request, messages.SUCCESS, "Added patient " + form.cleaned_data['first_name'] + " " + form.cleaned_data['last_name'])
            return HttpResponseRedirect(reverse('patient.views.list_patients'))
        else:
            messages.add_message(request, messages.ERROR, "Failed to add patient!")
            context['patient_form'] = form
    else:
        context['patient_form'] = BasicPatientForm()
    return render_to_response("patient/new_patient.html", context_instance=context)

@login_required
def single_case(request, case_id):
    case = CommCareCase.get(case_id)
    pat = BasePatient.get_typed_from_dict(BasePatient.get_db().get(case.patient_id))
    return render_to_response("shinepatient/single_case.html",
                              {"patient": pat, "case": case,
                               "json_case": json.dumps(case.to_json())}, 
                              context_instance=RequestContext(request))
    