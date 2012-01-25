#from provider.models import Provider
import logging
import pdb
from django.contrib.auth.models import AnonymousUser
from django.utils.hashcompat import sha_constructor
from carehqapp import constants
from patient.models import Patient

#http://www.djangosnippets.org/snippets/1661/
#from django.contrib.sessions.middleware import SessionMiddleware 
from django.core.exceptions import ObjectDoesNotExist
from permissions.models import Actor, PrincipalRoleRelation, Role
from django.contrib.auth.middleware import AuthenticationMiddleware
import settings

CACHED_CURRENT_ACTOR = "_cached_current_actor"
CACHED_CURRENT_TENANT = "_cached_current_tenant"
CACHED_ACTORS = "_cached_actors"
COOKIE_ACTOR_CONTEXT = "actor_context"

class LazyActors(object):
    """
    These are following the precedence for LazyUser in the django authehtnication middleware
    but, until something is made more clear on why it's necessary, we'll just do direct assignment

    For more reference see from django.contrib.auth.middleware.AuthenticationMiddleware
    """
    def __get__(self, request, obj_type=None):
        if not hasattr(request, CACHED_ACTORS):
            request._cached_actors = Actor.objects.filter(user=request.user)
        return request._cached_actors


def is_actor_cookie_synced(request, cached_actor):
    """
    Check the actor cookie value with the current cached actor value
    """
    actor_hash_from_cookie = request.COOKIES.get(COOKIE_ACTOR_CONTEXT, '')
    if actor_hash_from_cookie != '':
        cookie_actor_id, verify = actor_hash_from_cookie.split('.')
        #verify the hash
        if sha_constructor(cookie_actor_id+settings.SECRET_KEY).hexdigest() == verify:
            #ok, it passes hash muster, let's verify the IDS are identical
            if cookie_actor_id == cached_actor.id:
                return True
    return False


def get_current_actor_from_cookie(request):
    """
    Efficiently retrieve the current actor from the cookie
    """
    actor_hash_from_cookie = request.COOKIES.get(COOKIE_ACTOR_CONTEXT, '')
    actor_to_use = None
    if actor_hash_from_cookie != '':
        actor_id, verify = actor_hash_from_cookie.split('.')
        #verify the hash
        if sha_constructor(actor_id+settings.SECRET_KEY).hexdigest() == verify:
            try:
                actor_to_use = Actor.objects.get(id=actor_id)
            except Actor.DoesNotExist:
                return None
        else:
            logging.debug("Error, hash mismatch of cookie")
    if actor_to_use is None:
        if request.actors.count() > 0:
            actor_to_use = request.actors[0]
    return actor_to_use


#        override_actor_id = request.GET.get("choose_actor", None) #check to make sure user has his actor
#        if override_actor_id is not None:
#            actor_to_use = Actor.objects.get(id=override_actor_id)
#            set_cookie=True
#        else:
#override actor is None get it from cookie
    pass


class LazyCurrentActor(object):
    def __get__(self, request, obj_type=None):
        #check cookie status on current user
        if not hasattr(request, CACHED_CURRENT_ACTOR):
            request._cached_current_actor = get_current_actor_from_cookie(request)
        else:
            #sanity check - verify that cached value and cookie are in sync
            if not is_actor_cookie_synced(request, request._cached_current_actor):
                request._cached_current_actor = get_current_actor_from_cookie(request)
        return request._cached_current_actor


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
        if not isinstance(request.user, AnonymousUser): #CareHQ Identity Middleware requires the user be logged in.
            request.__class__.actors = LazyActors()
            request.__class__.current_actor = LazyCurrentActor()
        return None

    def process_response(self, request, response):
        #if the request's cookie and the cookie value are not in sync, or if the cookie doesn't exist, set the cookie here.
        if not hasattr(request, 'user'):
            return response
        if not isinstance(request.user, AnonymousUser): #CareHQ Identity Middleware requires the user be logged in.
            if response.cookies.has_key(COOKIE_ACTOR_CONTEXT):
                if hasattr(request, CACHED_CURRENT_ACTOR):
                    delattr(request, CACHED_CURRENT_ACTOR)
                return response
            requests_cookie = request.COOKIES.get(COOKIE_ACTOR_CONTEXT, None)
            if requests_cookie is None:
                #no cookie at all, generate the default cookie
                if hasattr(request, 'actors'):
                    if request.actors.count() > 0:
                        actor_to_use = request.actors[0]
                        actor_context_cookie = '%s.%s' % (actor_to_use.id, sha_constructor(actor_to_use.id + settings.SECRET_KEY).hexdigest())
                    else:
                        actor_context_cookie = ''
                    response.set_cookie(COOKIE_ACTOR_CONTEXT, actor_context_cookie)
        else:
            response.delete_cookie(COOKIE_ACTOR_CONTEXT)
        return response

        
        
            