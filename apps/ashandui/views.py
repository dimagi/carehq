from django.contrib.auth.decorators import  login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.models import User
from forms import AddProviderForm
from django.db.models import Q
from forms import LinkProviderForm, LinkProviderForm
from clinical_core.actors.models.roles import Doctor
from clinical_core.patient.models.djangomodels import Patient
from lib.crumbs import crumbs
from lib.jsonview import render_to_json
from django.shortcuts import get_object_or_404
from django.contrib import messages

@crumbs("Add Provider", "addProvider", "home")
@login_required
def addProvider(request, template="ashandui/addProvider.html"):
    context = RequestContext(request)
    if request.method == 'POST':
        form = AddProviderForm(data=request.POST)
        if form.is_valid():
            u = User()
            u.first_name = form.cleaned_data['first_name']
            u.last_name = form.cleaned_data['last_name']
            u.username = form.cleaned_data['username']
            u.set_password()
            u.save()
            d = Doctor()
            d.title = form.cleaned_data['title']
            d.department = form.cleaned_data['department']
            d.specialty = form.cleaned_data['specialty']
            d.user = u
            d.save()
            messages.add_message(request, messages.SUCCESS, "Added provider " + u.first_name + " " + u.last_name + " to the system.")

            return HttpResponseRedirect("/")
        else:
            messages.add_message(request, messages.ERROR, "Failed to add provider.")
            context['form'] = form
            return render_to_response(template,context)
    else:
        context['form'] = AddProviderForm()
    return render_to_response(template, context)


def formatProvidersList(query):
    return [{'first_name': d.user.first_name,
                'last_name': d.user.last_name,
                'id': d.id} for d in getProviders(query)]

def formatProvidersAutocomplete(query):
    return [{'value': d.id, 'label': d.user.first_name + " " + d.user.last_name} for d in getProviders(query)]
    

def getProviders(query):
    if query is None or query == "_all":
        results = Doctor.objects.all()
    else:
        results =  Doctor.objects.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query))
    return results

@render_to_json()
def providerSearchAjax(request):
    if request.method == 'GET':
        query = request.GET.get("query")
        return formatProvidersList(query)
    return formatProvidersList(None)


@render_to_json()
def providerListQueryAjax(request, term):
    if request.method == 'GET':
        term = request.GET.get("term")
        return formatProvidersAutocomplete(term)
    return formatProvidersAutocomplete(term)

@crumbs("Provider Search", "providerSearch", None)
def providerSearch(request, template="ashandui/providerSearch.html"):
    context = RequestContext(request)
    if 'query' in request.GET:
        # manual search performed
        context['providers'] = formatProvidersList(query)
    else:
        context['providers'] = [{'first_name': d.user.first_name, 'last_name': d.user.last_name} for d in Doctor.objects.all()]
    return render_to_response(template, context)

@crumbs("Provider Patients", "providerPatients", None)
def providerPatients(request, doctorId, template="ashandui/providerPatients.html"):
    context = RequestContext(request)
    doctor = get_object_or_404(Doctor, id=doctorId)
    context['doctor'] = doctor
    patients = get_object_or_404(Actor, role=doctor).patients.all()
    if patients:
        context['patients'] = patients
    return render_to_response(template, context)


def editCareteam(request, patientId, template="ashandui/providerLink.html"):
    context = RequestContext(request)
    patient = get_object_or_404(Patient, id=patientId)
    if request.method == 'POST':
        doctor_ids = request.POST.get("doctor")
        if isinstance(doctor_ids, list):
            doctors = map(Doctor.objects.get, doctor_ids)
        else:
            doctors = [Doctor.objects.get(id=doctor_ids)]
        for doctor in doctors:
            try:
                a = Actor.objects.get(role=doctor)
            except:
                a = Actor(role=doctor)
                a.save()
            pal = PatientActorLink(patient=patient, actor=a)
            pal.save()
    form = LinkProviderForm()
    form.patient = patientId

    # XXX Sorry
    doctorSet = list(Doctor.objects.all())
    careTeam = []
    for alreadyExists in map(lambda x: x.actor.role, PatientActorLink.objects.filter(patient=patient)):
        if alreadyExists.doctor in doctorSet:
            doctorSet.remove(alreadyExists.doctor)
            careTeam.append(alreadyExists.doctor)

    form.fields["doctor"].choices = ((d.id, d.user.first_name + " " + d.user.last_name) for d in doctorSet)
    context["form"] = form
    context["patient"] = patient
    context["careTeam"] = careTeam
    return render_to_response(template,context)

def ashandHome(request, template="ashandui/home.html"):
    context = RequestContext(request)
    return render_to_response(template,context)