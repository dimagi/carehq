from django.shortcuts import render_to_response
from ashandapp.datagrids import UserDataGrid
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
import logging
from django.contrib.auth.models import User
from casetracker.models import Case, Filter
from ashandapp.models import CaseProfile, CareTeam, ProviderLink
from provider.models import Provider
from patient.models import Patient
from casetracker.datagrids import CaseDataGrid, CaseEventDataGrid, FilterDataGrid
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from casetracker.queries.caseevents import get_latest_event, get_latest_for_cases

from ashandapp.forms.inquiry import NewInquiryForm
from ashandapp.forms.issue import NewIssueForm

 

@cache_page(60 * 5)
def all(request, template_name='ashandapp/user_datagrid.html'):
    return UserDataGrid(request).render_to_response(template_name)

#@cache_page(60 * 5)
@login_required
def single(request, user_id=None, sort=None):
    context = {}
    if user_id==None:
        user = request.user
    else:
        user = User.objects.get(id=user_id)
        
    context['selected_user'] = user
    try:
        template_name = "ashandapp/view_patient.html"
        patient = Patient.objects.all().get(user=user)
        context['is_patient'] = True
        context['patient'] = patient
        context['careteam'] = CareTeam.objects.get(patient=user)
        context['recent_events'] = get_latest_for_cases(context['careteam'].cases.all(), sort)
        cases = CareTeam.objects.get(patient=user).cases.all()  
        context['cases'] = cases      
        context['formatting'] = sort
        qtitle = "Cases for this patient"
    except:
        template_name = "ashandapp/view_user.html"
        context['is_patient'] = False
    
    #if this person is a provider, we need a better "gate" to differentiate
    providers = Provider.objects.all().filter(user=user)
    if len(providers) > 0:
        context['providers'] = providers
        template_name = "ashandapp/view_provider.html"
        
        #if a provider, do the provider queries        
        opened = Q(opened_by=user)
        last_edit = Q(last_edit_by=user)
        assigned = Q(assigned_to=user)
        
        cases = Case.objects.select_related('opened_by','last_edit_by','status').filter(opened | last_edit | assigned)
        context['cases'] = cases
        
        qtitle = "Cases for this provider"        
        #care_team_membership = ProviderLink.objects.filter(provider__id=user.id).values_list("care_team__id",flat=True)
        #context['care_teams'] = CareTeam.objects.select_related().filter(id__in=care_team_membership)
        care_team_membership = CareTeam.objects.filter(providers__in=providers)
        context['care_teams'] = care_team_membership
         
#    try:                
#        context['cases_datagrid'] = CaseDataGrid(request, qset=cases,qtitle=qtitle)
#    except Exception, e:
#        logging.error( "error with the stoopid case data grid %s" % str(e))
    return render_to_response(template_name, context, context_instance=RequestContext(request))

