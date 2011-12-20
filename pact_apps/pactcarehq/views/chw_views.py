from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from pactcarehq.views.submission_views import _get_submissions_for_user
from pactconfig import pact_api
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
    chws = pact_api.get_chws()
    def get_dashboard_for_chw(chw):
        results = CActivityDashboard.view('pactcarehq/chw_dashboard', key=chw.django_actor.user.username, group=True).all()
        if len(results) == 0:
            return {}
        else:
            return CActivityDashboard.wrap(results[0]['value'])
    context['chw_dashboard_dict'] = dict((x, get_dashboard_for_chw(x)) for x in chws)
    return render_to_response(template_name, context_instance=context)

@login_required
def chw_profile(request, chw_doc_id, template_name="pactcarehq/chw_profile.html"):
    context = RequestContext(request)
    chw = pact_api.get_chw(chw_doc_id)
    submits = _get_submissions_for_user(chw.django_actor.user.username)

    context['actor_doc'] = chw
    context['permissions_dict'] = pact_api.get_permissions_dict(chw)
    context['submit_arr'] = submits
    return render_to_response(template_name, context_instance=context)

