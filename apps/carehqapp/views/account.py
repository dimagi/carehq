from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.views import login as django_login
from django.contrib.auth.views import logout as django_logout
from lib.crumbs import crumbs
from django.conf import settings
#from auditcare.forms import SignaledAuthenticationForm
from auditcare.views import audit_login


@crumbs("My Profile", "my_profile", "home")
def my_profile(request, template_name = "carehqapp/my_profile.html"):
#   request.breadcrumbs("Profile", reverse(my_profile))
    context = RequestContext(request)
    return render_to_response(template_name, context_instance=context)

def login(req, template_name="/registration/login.html"):
    return audit_login(req, template_name)