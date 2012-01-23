# To manage patient views for create/view/update you need to implement them directly in your patient app
from datetime import datetime
import logging
import urllib
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from patient.models import Patient
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from patient.models import BasePatient
from patient.forms import BasicPatientForm
from django.contrib import messages
from patient.models import SimplePatient
from django.conf import settings



class PatientSingleView(TemplateView):
    template_name = 'patient/base_patient.html'
    patient_list_url = '/patient/list' #hardcoded from urls, because you can't do a reverse due to the urls not being bootstrapped yet.
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PatientSingleView,self).dispatch(*args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super(PatientSingleView, self).get_context_data(**kwargs)
        params = context['params']
        patient_guid =  params['patient_guid']
        pat = BasePatient.get_typed_from_dict(BasePatient.get_db().get(patient_guid))
        context['patient_doc'] = pat
        context['patient_django'] = Patient.objects.get(doc_id=pat._id)
        context['patient_list_url'] = self.patient_list_url
        return context



class PatientListView(TemplateView):
    """
    Generic class based view for viewing the patient list.
    """
    template_name="patient/patient_list.html"
    patient_type=None
    create_patient_viewname = settings.CAREHQ_CREATE_PATIENT_VIEW_NAME
    couch_view = 'patient/all'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PatientListView,self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PatientListView, self).get_context_data(**kwargs)
        view_results = BasePatient.get_db().view(self.couch_view, include_docs=True).all()
        pats = [BasePatient.get_typed_from_dict(row["doc"]) for row in view_results]

        if self.patient_type != None:
            pats = filter(lambda x: isinstance(x, self.patient_type), pats)
        context['patients'] = pats
        context['create_patient_url'] = reverse(self.create_patient_viewname)
        return context


@login_required
def list_patients(request, template="patient/patient_list.html"):
    view_results = BasePatient.get_db().view("patient/all", include_docs=True).all()
    pats = [BasePatient.get_typed_from_dict(row["doc"]) for row in view_results]
    create_patient_url = reverse(settings.CAREHQ_CREATE_PATIENT_VIEW_NAME)
    return render_to_response("patient/patient_list.html", 
                              {"patients": pats, 
                               "create_patient_url": create_patient_url},
                              context_instance=RequestContext(request))
@login_required
def new_patient(request, form_class=BasicPatientForm, validate_callback=None):
    """
    Basic patient view for creating a new patient, very barebones.
    """
    context = RequestContext(request)
    if request.method == 'POST':
        form = form_class(data=request.POST)
        # make patient
        if form.is_valid():
            newptdoc = SimplePatient()
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


