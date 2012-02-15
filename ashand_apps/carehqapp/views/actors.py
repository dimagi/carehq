import pdb
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from carehqadmin.forms.caregiver_form import CaregiverForm
from clinical_shared.utils import generator
from issuetracker.issue_constants import ISSUE_STATE_CLOSED
from issuetracker.models.issuecore import Issue

import urllib
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from actorpermission.models import ProviderActor, CaregiverActor
from carehq_core import carehq_constants, carehq_api
from carehqadmin.forms.provider_form import ProviderForm
from patient.models import  BasePatient
from permissions.models import Role, PrincipalRoleRelation, Actor
from permissions import utils as putils
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_POST
import logging
from tenant.models import Tenant



@login_required
def view_actor(request, actor_doc_id, view_mode, template_name="carehqapp/actor/carehq_actor_profile_base.html"):
    context = RequestContext(request)
    actor = Actor.objects.get(doc_id=actor_doc_id)
    context['actor_doc'] = actor.actordoc
    all_prrs = carehq_api.get_permissions(actor.actordoc, direct=True)


    if isinstance(actor.actordoc, CaregiverActor):
        if isinstance(request.current_actor.actordoc, CaregiverActor):
            #stiff security check
            raise PermissionDenied

    if request.current_actor.doc_id == actor_doc_id:
        is_me = True
    else:
        is_me = False

    context['is_me'] = is_me


    if isinstance(actor.actordoc, CaregiverActor):
        context['info_block_perms'] = all_prrs.filter(role__name=carehq_constants.role_caregiver)

    if view_mode == '':
        view_mode = 'networks'
    elif view_mode == 'issues':
        issues = Issue.objects.get_relevant(actor)
        context['issues'] = issues
        template_name = "carehqapp/actor/carehq_actor_profile_issues.html"
    if view_mode == 'info':
        template_name = "carehqapp/actor/carehq_actor_profile_info.html"

    if view_mode == 'networks':
        #context['patient_careteam'] = carehq_api.get_careteam(pdoc)
        context['connections'] = all_prrs
        template_name = "carehqapp/actor/carehq_actor_profile_network.html"

    context['view_mode'] = view_mode
    return render_to_response(template_name, context, context_instance=RequestContext(request))


@login_required
@user_passes_test(lambda u: u.is_superuser)
def pt_new_or_link_actor(request, patient_guid, template="carehqapp/admin_patient_actor_management.html"):
    """
    Add a provider to a patient's careteam by linking a permission to the patient/actor pair
    """
    context = RequestContext(request)
    actor_type = request.GET.get('type', None)
    if not actor_type:
        return HttpResponse("An actor type must be returned")
    context['actor_type'] = actor_type
    pt = BasePatient.get_typed_from_id(patient_guid)
    ashand_tenant = Tenant.objects.get(name="ASHand")
    context['patient_doc'] = pt

    if actor_type == 'caregiver':
        form_class = CaregiverForm
        actor_type_class = CaregiverActor.__name__
    elif actor_type == 'provider':
        form_class=ProviderForm
        actor_type_class = ProviderActor.__name__

    all_actors = ProviderActor.view('actorpermission/all_actors', include_docs=True).all()
    filtered_actors = filter(lambda x: x['doc_type'] == actor_type_class, all_actors)
    context['actors'] = filtered_actors

    if request.method == "POST":
        form = form_class(ashand_tenant, data=request.POST)
        if form.is_valid():
            new_actor = form.save(commit=False)
            new_user=None
            if form.cleaned_data.get('new_user', False):
                new_user = User(username=form.cleaned_data['username'])
                new_user.first_name = new_actor.first_name
                new_user.last_name = new_actor.last_name
                new_user.email = new_actor.email

                random_password = generator.random_text(length=8)
                new_user.set_password(random_password)
                new_user.save()
                #new_user.set_password(None) #just use a random and do the password reset
            new_actor.save(ashand_tenant, user=new_user)
            if actor_type == "caregiver":
                carehq_api.add_caregiver_to_patient(pt, new_actor)
            elif actor_type == "provider":
                carehq_api.add_provider_to_patient(pt, new_actor)
            #return HttpResponseRedirect(reverse('view_pactpatient', kwargs={'patient_guid': patient_guid}) + "#ptabs=patient-careteam-tab")
            context['form'] = form_class(ashand_tenant)
            return render_to_response(template, context_instance=context)
        else:
            context['form'] = form
    else:
        context['form'] = form_class(ashand_tenant)


    return render_to_response(template, context_instance=context)



@login_required
@require_POST
def do_add_actor_to_patient(request):
    resp = HttpResponse()
    try:
        patient_guid = urllib.unquote(request.POST['patient_guid']).encode('ascii', 'ignore')
        pdoc = BasePatient.get_typed_from_id(patient_guid)
        provider_actor_uuid = urllib.unquote(request.POST['actor_uuid']).encode('ascii', 'ignore')
        provider_actor_django = Actor.objects.get(id=provider_actor_uuid)

        actor_type = request.POST.get('actor_type', None)
        if actor_type == 'caregiver':
            role_class = Role.objects.get(name=carehq_constants.role_caregiver)
        elif actor_type == 'provider':
            role_class = Role.objects.get(name=carehq_constants.role_provider)
        elif actor_type == 'externalprovider':
            role_class = Role.objects.get(name=carehq_constants.role_external_provider)
        else:
            raise Exception("Error on input of role class")
        putils.add_local_role(pdoc.django_patient, provider_actor_django, role_class)
        #return HttpResponseRedirect(reverse('view_pactpatient', kwargs={'patient_guid': patient_guid}) + "#ptabs=patient-careteam-tab")
        resp.write("Success")
    except Exception, e:
        print "wtf: %s" % e
        logging.error("Error getting args:" + str(e))
        resp.write("Error")
        #return HttpResponse("Error: %s" % (e))
    return resp


@login_required
@require_POST
def rm_actor_from_patient(request):
    resp = HttpResponse()
    try:
        patient_guid = urllib.unquote(request.POST['patient_guid']).encode('ascii', 'ignore')
        pdoc = BasePatient.get_typed_from_id(patient_guid)
        provider_actor_uuid = urllib.unquote(request.POST['actor_uuid']).encode('ascii', 'ignore')
        provider_actor_django = Actor.objects.get(id=provider_actor_uuid)
        role_class = Role.objects.get(name=carehq_constants.role_external_provider)
        #permissions.utils.add_local_role(pdoc.django_patient, provider_actor_django, role_class)
        ctype = ContentType.objects.get_for_model(pdoc.django_patient)
        PrincipalRoleRelation.objects.filter(role=role_class, actor=provider_actor_django, content_type=ctype, content_id=pdoc.django_uuid).delete()
        return HttpResponseRedirect(reverse('view_pactpatient', kwargs={'patient_guid': patient_guid}) + "#ptabs=patient-careteam-tab")
    except Exception, e:
        logging.error("Error getting args:" + str(e))
        #return HttpResponse("Error: %s" % (e))
    return resp

@login_required
@require_POST
def rm_actor(request):
    resp = HttpResponse()
    try:
        provider_actor_uuid = urllib.unquote(request.POST['actor_uuid']).encode('ascii', 'ignore')
        provider_actor_django = Actor.objects.get(id=provider_actor_uuid)
        provider_actor_django.delete()
        return HttpResponseRedirect(reverse('pact_providers'))
    except Exception, e:
        logging.error("Error getting args:" + str(e))
        #return HttpResponse("Error: %s" % (e))
    return resp





def view_add_actor(request, template="carehqapp/new_carehq_actor.html"):
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
