from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from carehq_core import carehq_api
from dimagi.utils.couch.pagination import ReportBase
from pactcarehq.views.submission_views import _get_submissions_for_user
from pactpatient.models import CActivityDashboard


@login_required
def chw_actor_list(request, template_name="pactcarehq/chw_actor_list.html"):
    context = RequestContext(request)
    chws = carehq_api.get_chws()
    def get_dashboard_for_chw(chw):
        results = CActivityDashboard.view('pactcarehq/chw_dashboard', key=chw.django_actor.user.username, group=True).all()
        if len(results) == 0:
            return {}
        else:
            return CActivityDashboard.wrap(results[0]['value'])
    context['chw_dashboard_dict'] = dict((x, get_dashboard_for_chw(x)) for x in chws)
    return render_to_response(template_name, context_instance=context)

@login_required
def new_chw(request, template="pactcarehq/new_chw.html"):
    pass

@login_required
def chw_profile(request, chw_doc_id, view_mode, template_name="pactcarehq/chw/pact_actor_profile_info.html"):
    context = RequestContext(request)
    chw = carehq_api.get_chw(chw_doc_id)


    #form for supervision
    #CHW Profile (web)
#Supervision section
#Track - date and type of supervision received
#History of trainings attended
#Options from each of patients (Discussed yes/no)
#Make some type of form - checkboxes
#Transition patient?  Or just a separate manual entry
#Service plan discussion - a form to be entered
#Finalize content on service plan
#Then decide if it should be phone form or webform
#Adding new information to provider profile
#Link to submissions
#Client Panel - their assigned patients.  Only include CURRENT patients (show/hide discharges)
#
#Connection to Supervision Tools
#Patient Profile & Service Plan (from previously entered service plans)

    context['actor_doc'] = chw
    context['username'] = chw.django_actor.user.username
    context['permissions_dict'] = carehq_api.get_permissions_dict(chw)

    if view_mode == '':
        view_mode = 'submissions'


    if view_mode == 'issues':
        template_name = 'pactcarehq/chw/pact_actor_profile_info.html'
    elif view_mode == 'supervision':
        template_name = 'pactcarehq/chw/pact_actor_profile_supervision.html'
    elif view_mode == 'network':
        template_name = 'pactcarehq/chw/pact_actor_profile_network.html'
    elif view_mode == 'submissions':
        template_name = 'pactcarehq/chw/pact_actor_profile_submissions.html'
    context['view_mode'] = view_mode
#    context['submit_arr'] = [1,2,3]
    return render_to_response(template_name, context_instance=context)





def new_chw(request):
    #form for: username, phone number email
    #create user
    #create chwactor document
    #cherry pick patients to attach to?
    #update workflow for patient change primary HP
    #change patient sidebar for primary_hp
    pass



