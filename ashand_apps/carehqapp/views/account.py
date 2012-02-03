from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.views import login as django_login
from django.contrib.auth.views import logout as django_logout
from lib.crumbs import crumbs
from django.conf import settings
#from auditcare.forms import SignaledAuthenticationForm


@login_required
def no_actor(request, template_name="carehqapp/no_actor.html"):
    context=RequestContext(request)
    return render_to_response(template_name, context_instance=context)

