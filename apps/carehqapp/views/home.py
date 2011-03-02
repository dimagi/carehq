from django.shortcuts import render_to_response
from django.template.context import RequestContext
from lib.crumbs import crumbs
from django.contrib.auth.decorators import login_required


@crumbs("Home", "home", None)
@login_required
def home_view(request, template_name="carehqapp/home.html"):
    context=RequestContext(request)
    user = request.user
    context['user'] = user
    return render_to_response(template_name, context_instance=context)