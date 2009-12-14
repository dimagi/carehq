from django.shortcuts import render_to_response
from datagrids import UserDataGrid
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from models import CaseProfile
from casetracker.datagrids import CaseDataGrid, CaseEventDataGrid, FilterDataGrid

 
def datagrids(request, template_name='ashandapp/datagrids.html'):
    return UserDataGrid(request).render_to_response(template_name)

def styleguide(request, template_name="ashandapp/styleguide.html"):
    context = {}
    return render_to_response(template_name, context)


@login_required
def dashboard(request, template_name="ashandapp/dashboard.html"):
    context = {}
    user = request.user
    profile = CaseProfile.objects.get(user = user)
    filter_datagrid = CaseDataGrid(request, qset=profile.last_filter.get_filter_queryset(), qtitle=profile.last_filter.description)
    
    context['filter_datagrid'] = filter_datagrid
    context['profile'] = profile    
    context['filter'] = profile.last_filter
    return render_to_response(template_name, context, context_instance=RequestContext(request))