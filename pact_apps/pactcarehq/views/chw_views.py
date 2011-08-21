from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template.context import RequestContext
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
