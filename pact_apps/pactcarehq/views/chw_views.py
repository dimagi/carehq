from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from carehq_core import carehq_api
from pactcarehq.views.submission_views import _get_submissions_for_user
from pactpatient.models.pactmodels import CActivityDashboard

@login_required
def chw_list(request, template_name="pactcarehq/chw_list.html"):
    """A list of all users"""
    context = RequestContext(request)
    q_users = list(User.objects.all().filter(is_active=True).values_list('username', flat=True))

    users = []
    for u in q_users:
        if u.count("_") > 0:
            continue
        users.append(u.encode('ascii'))
    users.sort()

    chw_dashboards = CActivityDashboard.view('pactcarehq/chw_dashboard', keys=users, group=True).all()

    username_dashboard_dict = {}
    for reduction in chw_dashboards:
        chw_username = reduction['key']
        dashboard = CActivityDashboard.wrap(reduction['value'])
        username_dashboard_dict[chw_username] = dashboard
    context['chw_dashboards'] = []
    for uname in users:
        if username_dashboard_dict.has_key(uname):
            context['chw_dashboards'].append((uname, username_dashboard_dict[uname]))
        else:
            context['chw_dashboards'].append((uname, None))
    return render_to_response(template_name, context_instance=context)

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
def chw_api(request, chw_doc_id, template='pactcarehq/partials/ajax_form.html'):
    pass

@login_required
def new_chw(request, template="pactcarehq/new_chw.html"):
    pass

@login_required
def chw_profile(request, chw_doc_id, template_name="pactcarehq/chw_profile.html"):
    context = RequestContext(request)
    chw = carehq_api.get_chw(chw_doc_id)
#    submits = _get_submissions_for_user(chw.django_actor.user.username)


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
    context['permissions_dict'] = carehq_api.get_permissions_dict(chw)
#    context['submit_arr'] = submits
    context['submit_arr'] = [1,2,3]
    return render_to_response(template_name, context_instance=context)

def new_chw(request):
    #form for: username, phone number email
    #create user
    #create chwactor document
    #cherry pick patients to attach to?
    #update workflow for patient change primary HP
    #change patient sidebar for primary_hp
    pass