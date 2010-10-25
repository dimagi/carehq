#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib.auth.views import login as django_login
from django.contrib.auth.views import logout as django_logout
from django.views.decorators.csrf import csrf_protect

import settings

@csrf_protect
def login(req, template_name=settings.LOGIN_TEMPLATE):
    '''Login to carehq'''
    # this view, and the one below, is overridden because 
    # we need to set the base template to use somewhere  
    # somewhere that the login page can access it.    
    
    kwargs = {"template_name" : template_name}
    return django_login(req, **kwargs)

@csrf_protect
def logout(req, template_name=settings.LOGGEDOUT_TEMPLATE):
    '''Logout of carehq'''
 
    return django_logout(req, **{"template_name" : template_name})