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
def home_news(request, template_name='carehqapp/home.html'):
    context = RequestContext(request)
    context['title'] = "News Feed"
    if request.current_actor.is_patient:
        patient = request.current_actor.actordoc.get_django_patient()
        context['issues'] = Issue.objects.filter(patient=patient)
    else:
        context['issues'] = Issue.objects.care_issues(request.current_actor)
    return render_to_response(template_name, context_instance=context)

