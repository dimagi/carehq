from django.shortcuts import render_to_response

from django.contrib.auth.decorators import login_required
from django.template import RequestContext
import logging
from django.contrib.auth.models import User
from casetracker.models import Case, Filter
from ashandapp.models import CaseProfile, CareTeam,ProviderLink
from provider.models import Provider
from patient.models import Patient
from casetracker.datagrids import CaseDataGrid, CaseEventDataGrid, FilterDataGrid
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from casetracker.queries.caseevents import get_latest_event, get_latest_for_cases

from ashandapp.forms.issue import NewIssueForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

def new_issue(request, careteam_id, template_name="ashandapp/activities/issue/new_issue.html"):
    context = {}    
    careteam=CareTeam.objects.get(id=careteam_id)
    context['form'] = NewIssueForm(careteam=careteam)
    
    if request.method == 'POST':
        form = NewIssueForm(data=request.POST, careteam=CareTeam.objects.get(id=careteam_id))
        if form.is_valid():
            newcase = form.get_case(request)        
            newcase.save()
            careteam.cases.add(newcase)
            
            return HttpResponseRedirect(reverse('view-careteam', kwargs= {'careteam_id': careteam_id}))
        else:
            context['form'] = form
    
    return render_to_response(template_name, context, context_instance=RequestContext(request)) 