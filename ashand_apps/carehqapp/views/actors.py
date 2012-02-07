from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.models import User
from carehq_core import carehq_api
from issuetracker.feeds.issueevents import get_sorted_issueevent_dictionary
from issuetracker.issue_constants import ISSUE_STATE_CLOSED
from issuetracker.models.issuecore import Issue
from issuetracker.queries.issueevents import get_latest_for_issues
from patient.models import Patient
from permissions.models import Actor


@login_required
def view_actor(request, actor_doc_id, view_mode, template_name="carehqapp/carehq_actor_profile.html"):
    context = RequestContext(request)
    actor = Actor.objects.get(doc_id=actor_doc_id)
    context['actor_doc'] = actor.actordoc
    context['permissions_dict'] = carehq_api.get_permissions_dict(actor.actordoc)

    context['view_mode'] = view_mode
    context['is_me'] = is_me
    pdoc = context['patient_doc']
    dj_patient = context['patient_django']

    view_mode = self.kwargs.get('view_mode', '')
    if view_mode == '':
        view_mode = 'info'
    elif view_mode == 'issues':
        context['filter'] = request.GET.get('filter', 'recent')
    issues = Issue.objects.filter(patient=dj_patient)
    if context['filter']== 'closed':
        issues = issues.filter(status=ISSUE_STATE_CLOSED)
    elif context['filter'] == 'recent':
        issues = issues.order_by('-last_edit_date')
    elif context['filter'] == 'open':
        issues = issues.exclude(status=ISSUE_STATE_CLOSED)

        context['issues'] = issues
        self.template_name = "carehqapp/patient/carehq_patient_issues.html"
    if view_mode == 'info':
        self.template_name = "carehqapp/patient/carehq_patient_info.html"

    if view_mode == 'careteam':
        context['patient_careteam'] = carehq_api.get_careteam(pdoc)
        self.template_name = "carehqapp/patient/carehq_patient_careteam.html"

    if view_mode == 'careplan':
        self.template_name = "carehqapp/patient/carehq_patient_careplan.html"

    if view_mode == 'submissions':
        viewmonth = int(request.GET.get('month', date.today().month))
        viewyear = int(request.GET.get('year', date.today().year))
        sk = ['Test000001', viewyear, viewmonth, 0]
        ek = ['Test000001', viewyear, viewmonth, 31]



    return render_to_response(template_name, context, context_instance=RequestContext(request))

