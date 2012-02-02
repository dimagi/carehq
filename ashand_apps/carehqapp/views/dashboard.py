from django.shortcuts import render_to_response
from django.template.context import  RequestContext
from clinical_shared.decorators import actor_required
from issuetracker.models.issuecore import Issue
from clinical_core.feed.models import FeedEvent
from django.contrib.auth.decorators import login_required

@login_required
@actor_required
def home_news(request, template_name='carehqapp/home.html'):
    context = RequestContext(request)
    context['title'] = "News Feed"
    if request.current_actor.is_patient:
        patient = request.current_actor.actordoc.get_django_patient()
        context['issues'] = Issue.objects.filter(patient=patient)
    else:
        context['issues'] = Issue.objects.care_issues(request.current_actor)
    return render_to_response(template_name, context_instance=context)

