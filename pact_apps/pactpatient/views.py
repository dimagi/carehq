# Create your views here.
from django.contrib.auth.decorators import  login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from pactpatient.forms import PactPatientForm
from patient.models import Patient
import urllib
from patient.models import CPhone
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
            newpatient.couchdoc.pact_id = form.cleaned_data['pact_id']
            newpatient.couchdoc.arm = form.cleaned_data['arm']
            newpatient.couchdoc.gender = form.cleaned_data['gender']
            newpatient.couchdoc.birthdate = form.cleaned_data['birthdate']
            newpatient.couchdoc.art_regimen = form.cleaned_data['art_regimen']
            newpatient.couchdoc.non_art_regimen = form.cleaned_data['non_art_regimen']
            newpatient.couchdoc.primary_hp = form.cleaned_data['primary_hp']
            newpatient.couchdoc.first_name = form.cleaned_data['first_name']
            newpatient.couchdoc.last_name = form.cleaned_data['last_name']
            newpatient.save()
            messages.add_message(request, messages.SUCCESS, "Added patient " + form.cleaned_data['first_name'] + " " + form.cleaned_data['last_name'])
            return HttpResponseRedirect(reverse('pactcarehq.views.patient_view', kwargs={'patient_id':newpatient.id}))
        else:
            messages.add_message(request, messages.ERROR, "Failed to add patient!")
            context['patient_form'] = form
    else:
        context['patient_form'] = PactPatientForm()
    return render_to_response(template_name, context_instance=context)

