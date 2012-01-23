import logging
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import render_to_response
from django.template.context import  RequestContext
from django.utils.hashcompat import sha_constructor
from carehq_core import carehq_constants, carehq_api
from issuetracker.models.issuecore import Issue
from clinical_core.feed.models import FeedEvent
from lib.crumbs import crumbs
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from patient.models import Patient
from permissions.models import Role, PrincipalRoleRelation, Actor
import settings

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
def issue_dashboard(request, template_name='carehqapp/issue_home.html'):
    context = RequestContext(request)
#    user_actors = Actor.objects.filter(user=request.user)
#    proles = PrincipalRoleRelation.objects.filter(actor__in=user_actors)
#    #hack hack
#    patient_role = Role.objects.get(name=carehq_constants.role_patient)
#    provider_role = Role.objects.get(name=carehq_constants.role_provider)
#    caregiver_role = Role.objects.get(name=carehq_constants.role_caregiver)
#    primary_provider_role = Role.objects.get(name=carehq_constants.role_primary_provider)
#    context['title'] = "My Cases"
#
#
#    if request.is_patient:
#        patient = proles.filter(role=patient_role)[0].content
#        issues = Issue.objects.all().filter(patient=patient).select_related()
#        context['issues'] = issues
#
#    elif request.is_caregiver or request.is_provider or request.is_primary:
#        #get all patients under my care and get their issues
#        qprov = Q(role=provider_role)
#        qcg = Q(role=caregiver_role)
#        qprim = Q(role=primary_provider_role)
#        patient_ids= proles.filter(qprov|qcg|qprim).values_list('content_id', flat=True)
#        issues = Issue.objects.all().filter(patient__id__in=patient_ids).select_related()
#
#        prov_cg_actors = proles.filter(qprov|qcg|qprim).values_list('actor', flat=True)
#        qmine = Q(opened_by__in=prov_cg_actors)
#        qassigned = Q(assigned_to__in=prov_cg_actors)
#
#        context['issues']=issues.filter(qmine|qassigned)


    current_actors = request.actors
    return render_to_response(template_name, context_instance=context)




@login_required
def home_news(request, template_name='carehqapp/home.html'):
    context = RequestContext(request)
    context['title'] = "News Feed"
    context['issues'] = Issue.objects.care_issues(request.current_actor)

#    if request.is_patient:
#        patient = proles.filter(role=patient_role)[0].content
#        issues = Issue.objects.all().filter(patient=patient).select_related()
#        context['issues'] = issues
#
#    elif request.is_caregiver or request.is_provider or request.is_primary:
#        #get all patients under my care and get their issues
#        qprov = Q(role=provider_role)
#        qcg = Q(role=caregiver_role)
#        qprim = Q(role=primary_provider_role)
#        patient_ids= proles.filter(qprov|qcg|qprim).values_list('content_id', flat=True)
#        issues = Issue.objects.all().filter(patient__id__in=patient_ids).select_related()
#
#
#

    #check for existing actor_context cookie, else set it


#    response = render_to_response(template_name, context_instance=context)
    return render_to_response(template_name, context_instance=context)
#    set_actor_id = request.GET.get('set_actor', None)
#    if set_actor_id is not None:
#        #verify actor is kosher
#        actor_to_use = Actor.objects.get(id=set_actor_id)
#        if actor_to_use.user != request.user:
#            response.delete_cookie('actor_context')
#        #generate default cookie
#        actor_context_cookie = '%s.%s' % (actor_to_use.id, sha_constructor(actor_to_use.id + settings.SECRET_KEY).hexdigest())
#        response.set_cookie('actor_context', actor_context_cookie)
#        response._set_cookie=actor_context_cookie
#    return response


