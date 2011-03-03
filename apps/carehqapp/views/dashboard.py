from django.shortcuts import render_to_response
from django.template.context import  RequestContext
from clinical_core.feed.models import FeedEvent
from lib.crumbs import crumbs
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

@crumbs("Dashboard", "dashboard", "home")
@login_required
def dashboard_view(request, template_name = "carehqapp/dashboard.html"):
    context = RequestContext(request)
    user = request.user
    context['user'] = user
    events = FeedEvent.objects.filter(subject__user=user).order_by('created')[:5]
    context['events'] = events
    print events
    return render_to_response(template_name, context_instance=context)



