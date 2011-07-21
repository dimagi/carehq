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
from patient.models.patientmodels import SimplePatient
from django.conf import settings



class PatientSingleView(TemplateView):
    template_name = 'patient/single_patient.html'
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PatientSingleView,self).dispatch(*args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super(PatientSingleView, self).get_context_data(**kwargs)
        params = context['params']
        patient_guid =  params['patient_guid']
        pat = BasePatient.get_typed_from_dict(BasePatient.get_db().get(patient_guid))
        context['patient'] = pat
        return context



class PatientListView(TemplateView):
    """
    Generic class based view for viewing the patient list.
    """
    template_name="patient/patient_list.html"
    patient_type=None
    create_patient_viewname = settings.CAREHQ_CREATE_PATIENT_VIEW_NAME

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PatientListView,self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PatientListView, self).get_context_data(**kwargs)
        view_results = BasePatient.get_db().view("patient/all", include_docs=True).all()
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
def new_patient(request):
    """
    Basic patient view for creating a new patient, very barebones.
    """
    context = RequestContext(request)
    if request.method == 'POST':
        form = BasicPatientForm(data=request.POST)
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

@login_required
def single_patient(request, patient_id, template="patient/single_patient.html"):
    """Where patient_guid is the doc_id of the patient.
    """
    pat = BasePatient.get_typed_from_dict(BasePatient.get_db().get(patient_guid))
    return render_to_response(template, {"patient": pat},
                              context_instance=RequestContext(request))

@login_required
def remove_phone(request):
    if request.method == "POST":
        try:
            patient_id = urllib.unquote(request.POST['patient_id']).encode('ascii', 'ignore')
            patient = Patient.objects.get(id=patient_id)
            phone_id = urllib.unquote(request.POST['phone_id']).encode('ascii', 'ignore')
            for i, p in enumerate(patient.couchdoc.phones):
                if p.phone_id == phone_id:
                    p.deprecated=True
                    p.ended=datetime.utcnow()
                    p.edited_by = request.user.username
                    patient.couchdoc.phones[i] = p
                    patient.couchdoc.save()
            return HttpResponseRedirect(reverse('pactcarehq.views.patient_view', kwargs={'patient_id':patient_id}))
        except Exception, e:
            logging.error("Error getting args:" + str(e))
            #return HttpResponse("Error: %s" % (e))
    else:
        pass



@login_required
def remove_address(request):
    if request.method == "POST":
        try:
            patient_id = urllib.unquote(request.POST['patient_id']).encode('ascii', 'ignore')
            patient = Patient.objects.get(id=patient_id)
            address_id = urllib.unquote(request.POST['address_id']).encode('ascii', 'ignore')
            patient.couchdoc.remove_address(address_id)
            return HttpResponseRedirect(reverse('pactcarehq.views.patient_view', kwargs={'patient_id':patient_id}))
        except Exception, e:
            logging.error("Error getting args:" + str(e))
            #return HttpResponse("Error: %s" % (e))
    else:
        pass
