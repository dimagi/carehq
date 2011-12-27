from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from actorpermission.models.actortypes import CaregiverActor, CHWActor, ProviderActor
from carehq_core import carehq_constants
from carehqadmin.forms.actor_form import get_actor_form
import permissions
from permissions.models import Role
from tenant.models import Tenant
from django.core.urlresolvers import reverse




@login_required
@user_passes_test(lambda u: u.is_superuser)
def new_actor(request, tenant_id, template="carehqadmin/actors/new_actor.html"):
    provider_type = request.GET.get('type', None)

    if provider_type  is None:
        raise Http404
    elif provider_type == 'chw':
        doc_class = CHWActor
        role_class = Role.objects.get(name=carehq_constants.role_chw)
    elif provider_type == 'caregiver':
        doc_class = CaregiverActor
    elif provider_type == 'provider':
        doc_class = ProviderActor
        role_class = Role.objects.get(name=carehq_constants.role_external_provider)

    tenant = Tenant.objects.get(id=tenant_id)
    form_class = get_actor_form(doc_class)
    context = RequestContext(request)
    context['tenant'] = tenant

    if request.method == 'POST':
        form = form_class(tenant, data=request.POST)
        if form.is_valid():
            actor_instance = form.save(commit=False)
            actor_instance.save(tenant)
            permissions.utils.add_role(actor_instance.django_actor, role_class)
            return HttpResponseRedirect(reverse('manage_tenant', kwargs= {'tenant_id': tenant_id}))




        else:
            pass

    else:
        form = form_class(tenant)
    context['form'] = form
    return render_to_response(template, context)

