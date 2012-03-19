import pdb
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from actorpermission.models import ProviderActor
from carehq_core import carehq_api, carehq_constants
from carehqadmin.forms.provider_form import ProviderForm
from pactpatient.models import PactPatient
import permissions
from permissions.models import Role, PrincipalRoleRelation
from tenant.models import Tenant

@login_required
def pt_new_or_link_provider(request, patient_guid, template="pactcarehq/add_pact_provider_to_patient.html"):
    """
    Add a provider to a patient's careteam by linking a permission to the patient/actor pair
    """
    context = RequestContext(request)
    pt = PactPatient.get(patient_guid)
    pact_tenant = Tenant.objects.get(name="PACT")
    context['patient'] = pt

    if request.method == "POST":
        form = ProviderForm(pact_tenant, data=request.POST)
        if form.is_valid():
            provider_actor = form.save(commit=False)
            provider_actor.save(pact_tenant)
            carehq_api.add_external_provider_to_patient(pt, provider_actor)
            return HttpResponseRedirect(reverse('view_pactpatient', kwargs={'patient_guid': patient_guid, 'view_mode': ''}) + "#ptabs=patient-careteam-tab")
        else:
            context['form'] = form
    else:
        context['form'] = ProviderForm(pact_tenant)

    context['all_providers'] = ProviderActor.view('actorpermission/all_actors', include_docs=True).all()
    return render_to_response(template, context_instance=context)

def view_add_pact_provider(request, template="pactcarehq/new_pact_provider.html"):
    """
    List actors in system as well create them (unlinked)
    """
    context = RequestContext(request)
    pact_tenant = Tenant.objects.get(name="PACT")
    if request.method == "POST":
        form = ProviderForm(pact_tenant, data=request.POST)
        if form.is_valid():
            provider_actor = form.save(commit=False)
            provider_actor.save(pact_tenant)
            role_class = Role.objects.get(name=carehq_constants.role_external_provider)
            permissions.utils.add_role(provider_actor.django_actor, role_class)
            #note no local permission being added.
            return HttpResponseRedirect(reverse('pact_providers'))
        else:
            context['form'] = form
    else:
        context['form'] = ProviderForm(pact_tenant)

    context['provider_actors'] = carehq_api.get_external_providers()
    return render_to_response(template, context_instance=context)



def edit_provider(request, provider_guid, template="pactcarehq/edit_provider.html"):
    context = RequestContext(request)

    readonly = request.GET.get('readonly', False)
    actor_doc = ProviderActor.view('actorpermission/all_actors', key=provider_guid, include_docs=True).first()
    prrs = PrincipalRoleRelation.objects.filter(actor__id=actor_doc.actor_uuid)
    pact_tenant = Tenant.objects.get(name="PACT")
    context['perms'] = prrs

    if readonly:
        context['provider'] = actor_doc
    else:
        form = ProviderForm(pact_tenant, instance=actor_doc)
        if request.method == "POST":
            form = ProviderForm(pact_tenant, instance=actor_doc,data=request.POST)
            if form.is_valid():
                provider_actor = form.save(commit=False)
                provider_actor.save(pact_tenant)
                return HttpResponseRedirect(reverse('pact_providers'))
            else:
                context['form'] = form
        else:
            context['form'] = form
    return render_to_response(template, context_instance=context)
