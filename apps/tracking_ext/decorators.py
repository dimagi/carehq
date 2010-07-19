from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse,Http404
from ashandapp.models import CareTeam
import logging

def log_access(view_func):
    """
    Decorator for view - log each url and all params you're looking at.
    """
    def _log_access(request, *args, **kwargs):
#        print args
#        print kwargs
        return view_func(request, * args, **kwargs)
    return _log_access



