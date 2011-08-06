#from provider.models import Provider
from patient.models import Patient
from actors.models.roles import *

#http://www.djangosnippets.org/snippets/1661/
#from django.contrib.sessions.middleware import SessionMiddleware 
from django.core.exceptions import ObjectDoesNotExist

class LazyPatient(object):
    """
    These are following the precedence for LazyUser in the django authehtnication middleware
    but, until something is made more clear on why it's necessary, we'll just do direct assignment
    
    For more reference see from django.contrib.auth.middleware.AuthenticationMiddleware    
    """
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_patient'):
            try:
                request._cached_patient = Patient.objects.get(user=request.user)
            except ObjectDoesNotExist:
                return None
        return request._cached_patient


class LazyProvider(object):
    """
    These are following the precedence for LazyUser in the django authehtnication middleware
    but, until something is made more clear on why it's necessary, we'll just do direct assignment
    
    For more reference see from django.contrib.auth.middleware import AuthenticationMiddleware 
    """
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_provider'):
            try:
                request._cached_provider = Provider.objects.get(user=request.user)
            except ObjectDoesNotExist:
                return None
        return request._cached_provider

#http://www.djangosnippets.org/snippets/1661/

class AshandIdentityMiddleware(object):
    """
    Middleware for ashand to get identity information surrounding the logged in user.
    
    In the initial iteration, it will just the user's careteam membership and the general state of permissions
    granted to the logged in user.
    It should go without saying that this middleware should be enabled AFTER the authentication middleware as it
    assumes that there's a logged in user.
    """
    def process_request(self, request):
        assert hasattr(request, 'user'), "The ashand's identity middleware requires Django's authentication middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.auth.middleware.SessionMiddleware'."
        
        if not request.user or request.user.is_anonymous():
            #presume that the authentication middleware will handle this.
            return None
                
        #Check to see this person is a patient.
        is_patient = False
        is_provider = False
        is_caregiver = False    
        is_primary = False
         
        #unless there's a better explanation why the __class__ method should work...        
        #request.__class__.patient = LazyPatient()
        #if(request.patient):
        #    is_patient = True
        
        #unless there's a better explanation why the __class__ method should work...        
        #request.__class__.provider = LazyProvider()
        #if(request.provider):
        #    is_provider = True
        
        
        
        #############################
        #User is a patient
        try:
            request.patient = Patient.objects.get(user=request.user)
            request.my_careteam = CareTeam.objects.get(patient=request.patient)
            is_patient = True
        except ObjectDoesNotExist:
            pass
        
        
        #############################
        #User is a Provider
        try:
            request.provider = Doctor.objects.get(user=request.user)
            is_provider = True                        
            primary_careteams = CareTeamMember.objects.filter(role__user=request.user)
            if primary_careteams.count() > 0:
                is_primary = True        
        except ObjectDoesNotExist:
            pass
        
        ##############################
        #User is a caregiver
        try:
            request.caregiver = Caregiver.objects.get(user=request.user)
            is_caregiver = True
        except ObjectDoesNotExist:
            pass

#        request.patient_careteams = CareTeam.objects.all().filter(caregivers=request.user)
#        if request.patient_careteams.count() > 0:
#            is_caregiver = True
        
        request.is_provider = is_provider
        request.is_patient = is_patient
        request.is_caregiver = is_caregiver        
        request.is_primary = is_primary
#        print("Prov: %s Patient: %s Caregiver: %s Primary: %s" % (is_provider, is_patient, is_caregiver, is_primary))
             
        return None
            
        
        
            