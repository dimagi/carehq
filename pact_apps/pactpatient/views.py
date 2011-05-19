# Create your views here.
import uuid
from django.contrib.auth.decorators import  login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django_digest.decorators import httpdigest
from pactpatient.forms import PactPatientForm
from pactpatient.models.pactmodels import PactPatient
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
            newptdoc = PactPatient()
            newptdoc.pact_id = form.cleaned_data['pact_id']
            newptdoc.arm = form.cleaned_data['arm']
            newptdoc.gender = form.cleaned_data['gender']
            newptdoc.birthdate = form.cleaned_data['birthdate']
            newptdoc.art_regimen = form.cleaned_data['art_regimen']
            newptdoc.non_art_regimen = form.cleaned_data['non_art_regimen']
            newptdoc.primary_hp = form.cleaned_data['primary_hp']
            newptdoc.first_name = form.cleaned_data['first_name']
            newptdoc.last_name = form.cleaned_data['last_name']
            newptdoc.case_id = uuid.uuid1().hex
            newptdoc.save()
            messages.add_message(request, messages.SUCCESS, "Added patient " + form.cleaned_data['first_name'] + " " + form.cleaned_data['last_name'])
            return HttpResponseRedirect(reverse('pactcarehq.views.patient_view', kwargs={'patient_id':newptdoc.django_uuid}))
        else:
            messages.add_message(request, messages.ERROR, "Failed to add patient!")
            context['patient_form'] = form
    else:
        context['patient_form'] = PactPatientForm()
    return render_to_response(template_name, context_instance=context)
