from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import  Http404, HttpResponseRedirect
import logging



def actor_required(view_func):
    def _has_actor(request, *args, **kwargs):
        if not hasattr(request, 'current_actor') or request.current_actor is None:
            return HttpResponseRedirect(reverse('no_actor_profile'))
        return view_func(request, * args, **kwargs)
    return _has_actor

