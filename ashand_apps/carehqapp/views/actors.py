from django.contrib.auth.models import User
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
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_POST
import logging
from tenant.models import Tenant



@login_required
def view_actor(request, actor_doc_id, view_mode, template_name="carehqapp/carehq_actor_profile.html"):
    context = RequestContext(request)
    actor = Actor.objects.get(doc_id=actor_doc_id)
    context['actor_doc'] = actor.actordoc
    context['permissions_dict'] = carehq_api.get_permissions_dict(actor.actordoc)

    if request.current_actor.doc_id == actor_doc_id:
        is_me = True
    else:
        is_me = False

    context['view_mode'] = view_mode
    context['is_me'] = is_me

    if view_mode == '':
        view_mode = 'info'
    elif view_mode == 'issues':
        context['filter'] = request.GET.get('filter', 'recent')
        issues = Issue.objects.all()
        if context['filter']== 'closed':
            issues = issues.filter(status=ISSUE_STATE_CLOSED)
        elif context['filter'] == 'recent':
            issues = issues.order_by('-last_edit_date')
        elif context['filter'] == 'open':
            issues = issues.exclude(status=ISSUE_STATE_CLOSED)

            context['issues'] = issues
            template_name = "carehqapp/patient/carehq_patient_issues.html"
    if view_mode == 'info':
        template_name = "carehqapp/patient/carehq_patient_info.html"

    if view_mode == 'careteam':
        context['patient_careteam'] = carehq_api.get_careteam(pdoc)
        template_name = "carehqapp/patient/carehq_patient_careteam.html"

    if view_mode == 'careplan':
        template_name = "carehqapp/patient/carehq_patient_careplan.html"

    if view_mode == 'submissions':
#        viewmonth = int(request.GET.get('month', date.today().month))
#        viewyear = int(request.GET.get('year', date.today().year))
#        sk = ['Test000001', viewyear, viewmonth, 0]
#        ek = ['Test000001', viewyear, viewmonth, 31]
        pass

    return render_to_response(template_name, context, context_instance=RequestContext(request))


@login_required
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
                print random_password
                new_user.set_password(random_password)
                new_user.save()
                #new_user.set_password(None) #just use a random and do the password reset
            new_actor.save(ashand_tenant, user=new_user)
            carehq_api.add_external_provider_to_patient(pt, new_actor)
            #return HttpResponseRedirect(reverse('view_pactpatient', kwargs={'patient_guid': patient_guid}) + "#ptabs=patient-careteam-tab")
            context['form'] = form_class()
            return render_to_response(template, context_instance=context)
        else:
            context['form'] = form
    else:
        context['form'] = form_class(ashand_tenant)

    all_actors = ProviderActor.view('actorpermission/all_actors', include_docs=True).all()

    filtered_actors = filter(lambda x: x['doc_type'] == actor_type_class, all_actors)
    context['actors'] = filtered_actors
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
        role_class = Role.objects.get(name=carehq_constants.role_external_provider)
        putils.add_local_role(pdoc.django_patient, provider_actor_django, role_class)
        #return HttpResponseRedirect(reverse('view_pactpatient', kwargs={'patient_guid': patient_guid}) + "#ptabs=patient-careteam-tab")
        resp.write("Success")
    except Exception, e:
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
