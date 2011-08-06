from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from actorpermission.models.actortypes import ProviderActor
from carehqadmin.forms.actor_form import get_actor_form
from carehqadmin.forms.provider_form import ProviderForm
from pactconfig import constants
from pactpatient.models.pactmodels import PactPatient
import permissions
from permissions.models import Role
from tenant.models import Tenant

def pt_add_provider(request, patient_guid, template="pactcarehq/add_provider.html"):
    context = RequestContext(request)
    pt = PactPatient.get(patient_guid)
    context['patient_doc'] = pt

    if request.method == "POST":
        form = ProviderForm(data=request.POST)
        if form.is_valid():
            provider_actor = form.save(commit=False)
            provider_actor.save(Tenant.objects.get(name="PACT"))
            role_class = Role.objects.get(name=constants.role_external_provider)
            permissions.utils.add_local_role(pt.django_patient, provider_actor.django_actor, role_class)
            permissions.utils.add_role(provider_actor.django_actor, role_class)

            return HttpResponseRedirect(reverse('view_pactpatient', kwargs={'patient_guid': patient_guid}) + "#ptabs=patient-careteam-tab")
        else:
            context['form'] = form
    else:
        context['form'] = ProviderForm()

    context['all_providers'] = ProviderActor.view('actorpermission/all_actors').all()
    return render_to_response(template, context_instance=context)

