from django.shortcuts import render_to_response

from django.contrib.auth.decorators import login_required
from django.template import RequestContext
import logging
from django.http import HttpResponse
from django.contrib.auth.models import User
from casetracker.models import Case, Filter
from ashandapp.models import CaseProfile, CareTeam,ProviderLink
from provider.models import Provider
from patient.models import Patient
from casetracker.datagrids import CaseDataGrid, CaseEventDataGrid, FilterDataGrid
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from casetracker.queries.caseevents import get_latest_event, get_latest_for_cases

from ashandapp.forms.question import NewQuestionForm
from ashandapp.forms.issue import NewIssueForm

@login_required
def get_json_for_paging(request):
    
    user = request.user
    
    display_filter = None    
    start_index = None
    length = None
    
    try:
        profile = CaseProfile.objects.get(user = user)                
    except ObjectDoesNotExist:
        #make the new case profile
        profile = CaseProfile()
        profile.user = user
        profile.filter = Filter.objects.get(id=1)
        profile.last_filter = Filter.objects.get(id=1) #this is a nasty hack, as we're assuming id 1 is the reflexive one 
    
    
    if len(request.GET.items()) > 0:
            for item in request.GET.items():
                if item[0] == 'filter':
                    filter_id = item[1]    
                if item[0] == 'iDisplayStart':
                    start_index = item[1]
                if item[0] == 'iDisplayLength':
                    length = item[1]        
                    try:
                        display_filter = Filter.objects.get(id=filter_id)                                                
                    except:
                        pass
    else:
        display_filter = profile.last_filter
    
    filter = display_filter
    # add conditional to only work if display and start not null
    try:
        display_filter = display_filter.get_filter_queryset()[start_index:start_index + length]
    except:
        display_filter = display_filter.get_filter_queryset()[start_index:]  
    
    
    #build json_string with information from data    
    json_string = "{ \"aaData\": ["
   
    #adding user
    for case in display_filter:
        json_string += "["
        json_string += "\"%s %s\"," % (case.careteam_set.get().patient.first_name, case.careteam_set.get().patient.last_name)
        for col in filter.gridpreference.display_columns.all():
            json_string +=  "\"%s\"," % getattr(case, col.name)
        json_string += "],"
  
    #closing json_string
    json_string += "] }"
    
    return HttpResponse(json_string)

@login_required
#@cache_page(60 * 5)
def my_dashboard_tab(request, template_name="ashandapp/test.html"): 
 
    context = {}
    user = request.user
    
    display_filter = None    
        
    try:
        profile = CaseProfile.objects.get(user = user)                
    except ObjectDoesNotExist:
        #make the new case profile
        profile = CaseProfile()
        profile.user = user
        profile.filter = Filter.objects.get(id=1)
        profile.last_filter = Filter.objects.get(id=1) #this is a nasty hack, as we're assuming id 1 is the reflexive one 
    
    
    if len(request.GET.items()) > 0:
            for item in request.GET.items():
                if item[0] == 'filter':
                    filter_id = item[1]            
                    try:
                        display_filter = Filter.objects.get(id=filter_id)                                                
                    except:
                        pass
    else:
        display_filter = profile.last_filter
    
    
    #doing this on very load seems incredibly inefficient.  perhaps update the request object and cache stuff?
    profile.last_login = datetime.utcnow()
    profile.last_login_from = request.META['REMOTE_ADDR']
    profile.last_filter = display_filter
    profile.save()        
    
    shared_filters = Filter.objects.filter(shared=True)
    context['shared_filters'] = shared_filters
    
    context['display_filter'] = display_filter
        
    context['profile'] = profile    
    context['filter'] = profile.last_filter
    
    providers = Provider.objects.filter(user=user)
    if len(providers) > 0:
        context['providers'] = providers
        
        #commenting out because filters should do this now        
        #opened = Q(opened_by=user)
        #last_edit = Q(last_edit_by=user)
        #assigned = Q(assigned_to=user)        
        #cases = Case.objects.filter(opened | last_edit | assigned)
        #qtitle = "Cases for this provider"        
                
        careteam_membership = ProviderLink.objects.filter(provider__id=user.id).values_list("careteam__id",flat=True)
        context['careteams'] = CareTeam.objects.filter(id__in=careteam_membership)  
    return render_to_response(template_name, context, context_instance=RequestContext(request))

@login_required
def my_dashboard(request, template_name="ashandapp/dashboard.html"):
    context = {}
    user = request.user
    
    display_filter = None    
        
    try:
        profile = CaseProfile.objects.get(user = user)                
    except ObjectDoesNotExist:
        #make the new case profile
        profile = CaseProfile()
        profile.user = user
        profile.filter = Filter.objects.get(id=1)
        profile.last_filter = Filter.objects.get(id=1) #this is a nasty hack, as we're assuming id 1 is the reflexive one 
    
    
    if len(request.GET.items()) > 0:
            for item in request.GET.items():
                if item[0] == 'filter':
                    filter_id = item[1]            
                    try:
                        display_filter = Filter.objects.get(id=filter_id)                                                
                    except:
                        pass
                    
    else:
        display_filter = profile.last_filter
    
    
    #doing this on very load seems incredibly inefficient.  perhaps update the request object and cache stuff?
    profile.last_login = datetime.utcnow()
    profile.last_login_from = request.META['REMOTE_ADDR']
    profile.last_filter = display_filter
    profile.save()        
    
    shared_filters = Filter.objects.select_related('gridpreference').filter(shared=True)
    context['shared_filters'] = shared_filters
    
    context['display_filter'] = display_filter
    
    
    context['profile'] = profile    
    context['filter'] = profile.last_filter
    context['gridpreference'] = context['filter'].gridpreference
    
    providers = Provider.objects.filter(user=user)
    if len(providers) > 0:
        context['providers'] = providers
        
        #commenting out because filters should do this now        
        #opened = Q(opened_by=user)
        #last_edit = Q(last_edit_by=user)
        #assigned = Q(assigned_to=user)        
        #cases = Case.objects.filter(opened | last_edit | assigned)
        #qtitle = "Cases for this provider"        
                
        careteam_membership = ProviderLink.objects.filter(provider=request.provider).values_list("careteam__id",flat=True)
        context['careteams'] = CareTeam.objects.filter(id__in=careteam_membership)    
    return render_to_response(template_name, context, context_instance=RequestContext(request))
