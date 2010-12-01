# Create your views here.
from django.contrib.auth.decorators import permission_required, login_required
import json
from django.http import HttpResponseRedirect
from patient.models.couchmodels import CPhone, CAddress
import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from patient.forms import PactPatientForm

@login_required
def new_patient(request, template_name="patient/new_patient.html"):
    context = RequestContext(request)
    if request.method == 'POST':
        form = PactPatientForm(data=request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('pactcarehq.views.patient_view', kwargs={'patient_id':patient_id}))
        else:
            context['patient_form'] = form
    else:
        context['patient_form'] = PactPatientForm()
    return render_to_response(template_name, context_instance=context)
