from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.hashcompat import sha_constructor
from carehq_core import carehq_api
from permissions.models import Actor
import settings

@login_required
def landing(request, template='account/landing.html'):
    context = RequestContext(request)
    permissions = {}
    context['num_actors'] = len(request.actors)
    for actor in request.actors:
        permissions[actor] = carehq_api.get_permissions_dict(actor.actordoc)
    context['permissions'] = permissions


    return render_to_response(template, context)

@login_required
def set_current_actor(request, actor_id):
    response = HttpResponseRedirect(reverse('account_landing'))
    #verify actor is kosher
    actor_to_use = Actor.objects.get(id=actor_id)
    if actor_to_use.user != request.user:
        response.delete_cookie('actor_context')
        #generate default cookie
    actor_context_cookie = '%s.%s' % (actor_to_use.id, sha_constructor(actor_to_use.id + settings.SECRET_KEY).hexdigest())
    response.set_cookie('actor_context', actor_context_cookie)
    response._set_cookie=actor_context_cookie
    return response