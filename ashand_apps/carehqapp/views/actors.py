from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.models import User
from actorpermission.models import ProviderActor
from carehq_core import carehq_api
from carehqadmin.forms.provider_form import ProviderForm
from issuetracker.feeds.issueevents import get_sorted_issueevent_dictionary
from issuetracker.issue_constants import ISSUE_STATE_CLOSED
from issuetracker.models.issuecore import Issue
from issuetracker.queries.issueevents import get_latest_for_issues
from patient.models import Patient, BasePatient
from permissions.models import Actor
from tenant.models import Tenant


@login_required
def view_actor(request, actor_doc_id, view_mode, template_name="carehqapp/carehq_actor_profile.html"):
    context = RequestContext(request)
    actor = Actor.objects.get(doc_id=actor_doc_id)
    context['actor_doc'] = actor.actordoc
    context['permissions_dict'] = carehq_api.get_permissions_dict(actor.actordoc)

    context['view_mode'] = view_mode
    context['is_me'] = is_me
    pdoc = context['patient_doc']
    dj_patient = context['patient_django']

    view_mode = self.kwargs.get('view_mode', '')
    if view_mode == '':
        view_mode = 'info'
    elif view_mode == 'issues':
        context['filter'] = request.GET.get('filter', 'recent')
    issues = Issue.objects.filter(patient=dj_patient)
    if context['filter']== 'closed':
        issues = issues.filter(status=ISSUE_STATE_CLOSED)
    elif context['filter'] == 'recent':
        issues = issues.order_by('-last_edit_date')
    elif context['filter'] == 'open':
        issues = issues.exclude(status=ISSUE_STATE_CLOSED)

        context['issues'] = issues
        self.template_name = "carehqapp/patient/carehq_patient_issues.html"
    if view_mode == 'info':
        self.template_name = "carehqapp/patient/carehq_patient_info.html"

    if view_mode == 'careteam':
        context['patient_careteam'] = carehq_api.get_careteam(pdoc)
        self.template_name = "carehqapp/patient/carehq_patient_careteam.html"

    if view_mode == 'careplan':
        self.template_name = "carehqapp/patient/carehq_patient_careplan.html"

    if view_mode == 'submissions':
#        viewmonth = int(request.GET.get('month', date.today().month))
#        viewyear = int(request.GET.get('year', date.today().year))
#        sk = ['Test000001', viewyear, viewmonth, 0]
#        ek = ['Test000001', viewyear, viewmonth, 31]
        pass

    return render_to_response(template_name, context, context_instance=RequestContext(request))


@login_required
def pt_new_or_link_actor(request, patient_guid, template="carehqapp/admin_actor_management.html"):
    """
    Add a provider to a patient's careteam by linking a permission to the patient/actor pair
    """
    context = RequestContext(request)
    pt = BasePatient.get_typed_from_id(patient_guid)
    pact_tenant = Tenant.objects.get(name="ASHand")
    context['patient'] = pt

    if request.method == "POST":
        form = ProviderForm(pact_tenant, data=request.POST)
        if form.is_valid():
            provider_actor = form.save(commit=False)
            provider_actor.save(pact_tenant)
            carehq_api.add_external_provider_to_patient(pt, provider_actor)
            return HttpResponseRedirect(reverse('view_pactpatient', kwargs={'patient_guid': patient_guid}) + "#ptabs=patient-careteam-tab")
        else:
            context['form'] = form
    else:
        context['form'] = ProviderForm(pact_tenant)

    context['all_providers'] = ProviderActor.view('actorpermission/all_actors', include_docs=True).all()
    return render_to_response(template, context_instance=context)

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
