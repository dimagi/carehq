from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import  Http404, HttpResponseRedirect
import logging
from auditcare.middleware import AuditMiddleware

def actor_required(view_func):
    """
    Verify that an actor is needed for the view to run.
    """
    def _has_actor(request, *args, **kwargs):
        if not hasattr(request, 'current_actor') or request.current_actor is None:
            extra_info = {'current_actor': 'no_actor' }
            AuditMiddleware.do_process_view(request, view_func, args, kwargs, extra=extra_info)
            return HttpResponseRedirect(reverse('no_actor_profile'))

        actor_info = {'current_actor': request.current_actor.id }
        AuditMiddleware.do_process_view(request, view_func, args, kwargs, extra=actor_info)
        return view_func(request, *args, **kwargs)
    return _has_actor

