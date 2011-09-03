# Create your views here.
import uuid
from django.contrib.auth.decorators import  login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django_digest.decorators import httpdigest
from casexml.apps.case.models import CommCareCase
from pactpatient.forms import PactPatientForm
from pactpatient.models.pactmodels import PactPatient
from patient.models import Patient
import urllib
from patient.models import CPhone
from datetime import datetime, datetime
import logging
from django.contrib import messages

@login_required
def new_patient(request, template_name="pactpatient/new_pactpatient.html"):
    context = RequestContext(request)
    if request.method == 'POST':
        form = PactPatientForm("new", data=request.POST)
        #make patient
        if form.is_valid():
            newptdoc = form.save(commit=False)
#            newptdoc = PactPatient()
#            newptdoc.pact_id = form.cleaned_data['pact_id']
#            newptdoc.arm = form.cleaned_data['arm']
#            newptdoc.gender = form.cleaned_data['gender']
#            newptdoc.birthdate = form.cleaned_data['birthdate']
#            newptdoc.art_regimen = form.cleaned_data['art_regimen']
#            newptdoc.non_art_regimen = form.cleaned_data['non_art_regimen']
#            newptdoc.primary_hp = form.cleaned_data['primary_hp']
#            newptdoc.first_name = form.cleaned_data['first_name']
#            newptdoc.last_name = form.cleaned_data['last_name']
            newptdoc.case_id = uuid.uuid4().hex
            newptdoc.save()
            #now create a case for this
            case = CommCareCase()
            case._id = newptdoc.case_id
            case.start_date = datetime.utcnow().date()
            case.external_id = newptdoc.pact_id
            case.save()
            messages.add_message(request, messages.SUCCESS, "Added patient " + form.cleaned_data['first_name'] + " " + form.cleaned_data['last_name'])
            return HttpResponseRedirect(reverse('view_pactpatient', kwargs={'patient_guid':newptdoc._id}))
        else:
            messages.add_message(request, messages.ERROR, "Failed to add patient!")
            context['patient_form'] = form
    else:
        context['patient_form'] = PactPatientForm("new")

    return render_to_response(template_name, context_instance=context)
