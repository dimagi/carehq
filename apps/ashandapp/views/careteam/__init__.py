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
from ashandapp.decorators import is_careteam_member

from careplan.models import TemplateCarePlan


@login_required
@is_careteam_member
def single(request, careteam_id, template_name="ashandapp/view_careteam.html"):    
    context = {}
    careteam = CareTeam.objects.get(id=careteam_id)
    
    context['current_careteam'] = careteam
                
    cases = careteam.cases.all()
    context['cases'] = cases    
    context['patient']= careteam.patient
    
    context['careteam'] = careteam                
    cases = careteam.cases.all()
    context['cases'] = cases    
    
    context['careplan'] = TemplateCarePlan.objects.all()[0]
    context['show_children'] = True
    context['plan_items'] = context['careplan'].templatecareplanitemlink_set.all()    
    
    
    return render_to_response(template_name, context, context_instance=RequestContext(request))
