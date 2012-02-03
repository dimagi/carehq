#from provider.models import Provider
from carehqapp import constants
from patient.models import Patient

#http://www.djangosnippets.org/snippets/1661/
#from django.contrib.sessions.middleware import SessionMiddleware 
from django.core.exceptions import ObjectDoesNotExist
from permissions.models import Actor, PrincipalRoleRelation, Role
from django.contrib.auth.middleware import AuthenticationMiddleware

class LazyActors(object):
    """
    These are following the precedence for LazyUser in the django authehtnication middleware
    but, until something is made more clear on why it's necessary, we'll just do direct assignment

    For more reference see from django.contrib.auth.middleware.AuthenticationMiddleware
    """
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_actors'):
            request._cached_actors = Actor.objects.filter(user=request.user)
        return request._cached_actors

class CareHQIdentityMiddleware(object):
    """
    Middleware for ashand to get identity information surrounding the logged in user.
    
    In the initial iteration, it will just the user's careteam membership and the general state of permissions
    granted to the logged in user.
    It should go without saying that this middleware should be enabled AFTER the authentication middleware as it
    assumes that there's a logged in user.
    """
    def process_request(self, request):
        assert hasattr(request, 'user'), "The ashand's identity middleware requires Django's authentication middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.auth.middleware.SessionMiddleware'."
        request.__class__.actors = LazyActors()
        return None
            
        
        
            