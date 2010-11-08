from django.template.context import RequestContext
from django.shortcuts import render_to_response

def my_profile(request, template_name = "carehqapp/my_profile.html"):
    context = RequestContext(request)
    return render_to_response(template_name, context_instance=context)
