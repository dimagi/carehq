# Create your views here.
from django.contrib.auth.decorators import  login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from pactpatient.forms import PactPatientForm
from patient.models.djangomodels import Patient
import urllib
from patient.models.couchmodels import CPhone
from datetime import datetime, datetime
import logging
from django.contrib import messages

@login_required
def new_patient(request, template_name="patient/new_patient.html"):
    context = RequestContext(request)
    if request.method == 'POST':
        form = PactPatientForm(data=request.POST)
        #make patient
        if form.is_valid():
            newpatient = Patient()
            newpatient.cset_pact_id(form.cleaned_data['pact_id'])
            newpatient.cset_arm(form.cleaned_data['arm'])
            newpatient.cset_gender(form.cleaned_data['gender'])
            newpatient.cset_birthdate(form.cleaned_data['birthdate'])
            newpatient.cset_art_regimen(form.cleaned_data['art_regimen'])
            newpatient.cset_non_art_regimen(form.cleaned_data['non_art_regimen'])
            newpatient.cset_primary_hp(form.cleaned_data['primary_hp'])
            newpatient.cset_first_name(form.cleaned_data['first_name'])
            newpatient.cset_last_name(form.cleaned_data['last_name'])
            newpatient.save()
            messages.add_message(request, messages.SUCCESS, "Added patient " + form.cleaned_data['first_name'] + " " + form.cleaned_data['last_name'])
            return HttpResponseRedirect(reverse('pactcarehq.views.patient_view', kwargs={'patient_id':newpatient.id}))
        else:
            messages.add_message(request, messages.ERROR, "Failed to add patient!")
            context['patient_form'] = form
    else:
        context['patient_form'] = PactPatientForm()
    return render_to_response(template_name, context_instance=context)

