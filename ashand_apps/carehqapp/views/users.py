from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.models import User
from carehq_core import carehq_api
from issuetracker.feeds.issueevents import get_sorted_issueevent_dictionary
from issuetracker.queries.issueevents import get_latest_for_issues
from patient.models import Patient
from permissions.models import Actor


@login_required
def view_actor(request, actor_id, template_name="carehqapp/carehq_actor_profile.html"):
    context = RequestContext(request)
    #grr, this is django actor, not Actor doc_id
    actor = Actor.objects.get(id=actor_id)
    context['actor_doc'] = actor.actordoc
    context['permissions_dict'] = carehq_api.get_permissions_dict(actor.actordoc)
    return render_to_response(template_name, context, context_instance=RequestContext(request))

