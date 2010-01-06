from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse,Http404
from ashandapp.models import CareTeam
import logging

def is_careteam_member(view_func):
    def _is_member(request, careteam_id, *args, **kwargs):
        #get careteam id
        careteam = CareTeam.objects.get(id=careteam_id)
        
        #if it's the patient just return immediately
        if careteam.patient == request.user:
            return view_func(request, careteam_id, *args, **kwargs)        
        
        
        if careteam.providers.filter(user=request.user).count() == 0 and careteam.caregivers.filter(id=request.user.id).count() == 0:
            print "not the patient and not a provider or caregiver!"
            raise Http404    
        
        
        return view_func(request, careteam_id, * args, **kwargs)
    return _is_member


def provider_only(view_func):
    """
    Decorator for views that checks whether a user is an extuser.
    Redirecting to the no permissions page if necessary.
    """
    def _is_provider(request, *args, **kwargs):
        if not request.is_provider:
            raise Http404    
        return view_func(request, * args, **kwargs)
    return _is_provider

def caregiver_only(view_func):
    """
    Decorator for views that checks whether a user is an extuser.
    Redirecting to the no permissions page if necessary.
    """
    def _is_caregiver(request, *args, **kwargs):
        if not request.is_caregiver:
            raise Http404    
        return view_func(request, * args, **kwargs)
    return _is_caregiver

def patient_only(view_func):
    """
    Decorator for views that checks whether a user is an extuser.
    Redirecting to the no permissions page if necessary.
    """
    def _is_patient(request, *args, **kwargs):
        if not request.is_patient:
            raise Http404  
        return view_func(request, * args, **kwargs)
    return _is_patient
