from django.db.models.query_utils import Q
from django.shortcuts import render_to_response
from django.template.context import  RequestContext
from carehq_core import carehq_constants
from issuetracker.models.issuecore import Issue
from clinical_core.feed.models import FeedEvent
from lib.crumbs import crumbs
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from permissions.models import Role, PrincipalRoleRelation, Actor

@crumbs("Dashboard", "dashboard", "home")
@login_required
def dashboard_view(request, template_name = "carehqapp/dashboard.html"):
    context = RequestContext(request)
    user = request.user
    context['user'] = user
    events = FeedEvent.objects.filter(subject__user=user).order_by('created')[:5]
    context['events'] = events
    return render_to_response(template_name, context_instance=context)


@login_required
def ghetto_dashboard(request, template_name='carehqapp/ghetto_dashboard.html'):
    context = RequestContext(request)
    user_actors = Actor.objects.filter(user=request.user)
    proles = PrincipalRoleRelation.objects.filter(actor__in=user_actors)
    #hack hack
    patient_role = Role.objects.get(name=carehq_constants.role_patient)
    provider_role = Role.objects.get(name=carehq_constants.role_provider)
    caregiver_role = Role.objects.get(name=carehq_constants.role_caregiver)
    primary_provider_role = Role.objects.get(name=carehq_constants.role_primary_provider)
    context['title'] = "My Cases"


    if request.is_patient:
        patient = proles.filter(role=patient_role)[0].content
        issues = Issue.objects.all().filter(patient=patient).select_related()
        context['issues'] = issues

    elif request.is_caregiver or request.is_provider or request.is_primary:
        #get all patients under my care and get their issues
        qprov = Q(role=provider_role)
        qcg = Q(role=caregiver_role)
        qprim = Q(role=primary_provider_role)
        patient_ids= proles.filter(qprov|qcg|qprim).values_list('content_id', flat=True)
        issues = Issue.objects.all().filter(patient__id__in=patient_ids).select_related()

        prov_cg_actors = proles.filter(qprov|qcg|qprim).values_list('actor', flat=True)
        qmine = Q(opened_by__in=prov_cg_actors)
        qassigned = Q(assigned_to__in=prov_cg_actors)

        context['issues']=issues.filter(qmine|qassigned)
    return render_to_response(template_name, context_instance=context)


@login_required
def ghetto_news_feed(request, template_name='carehqapp/ghetto_dashboard.html'):
    context = RequestContext(request)
    user_actors = Actor.objects.filter(user=request.user)
    proles = PrincipalRoleRelation.objects.filter(actor__in=user_actors)
    #hack hack
    patient_role = Role.objects.get(name=carehq_constants.role_patient)
    provider_role = Role.objects.get(name=carehq_constants.role_provider)
    caregiver_role = Role.objects.get(name=carehq_constants.role_caregiver)
    primary_provider_role = Role.objects.get(name=carehq_constants.role_primary_provider)
    context['title'] = "News Feed (all patients)"


    if request.is_patient:
        patient = proles.filter(role=patient_role)[0].content
        issues = Issue.objects.all().filter(patient=patient).select_related()
        context['issues'] = issues

    elif request.is_caregiver or request.is_provider or request.is_primary:
        #get all patients under my care and get their issues
        qprov = Q(role=provider_role)
        qcg = Q(role=caregiver_role)
        qprim = Q(role=primary_provider_role)
        patient_ids= proles.filter(qprov|qcg|qprim).values_list('content_id', flat=True)
        issues = Issue.objects.all().filter(patient__id__in=patient_ids).select_related()



        context['issues']=issues
    return render_to_response(template_name, context_instance=context)

