from datetime import datetime
import logging

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse
from casetracker.models import Filter, Case, CaseEvent

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from provider.models import Provider


from ashandapp.models import CareTeam, ProviderRole, ProviderLink, CaregiverLink, CareRelationship,CaseProfile

from ashandapp.forms.question import NewQuestionForm
from ashandapp.forms.issue import NewIssueForm
from ashandapp.templatetags.filter_tags import case_column
from ashandapp.views.cases import queries


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
                if item[0] == 'start':
                    start_index = item[1]
                if item[0] == 'iDisplayLength':
                    length = item[1]        
                    try:
                        display_filter = Filter.objects.get(id=filter_id)                                                
                    except:
                        pass
    else:
        display_filter = profile.last_filter
    
    
    profile.last_login = datetime.utcnow()
    profile.last_login_from = request.META['REMOTE_ADDR']
    profile.last_filter = display_filter
    profile.save()       
    
    filter = display_filter
    
    # add pagination later...
    display_filter = display_filter.get_filter_queryset()
    # add conditional to only work if display and start not null
#    try:
#        display_filter = display_filter.get_filter_queryset()[start_index:start_index + length]
#    except:
#        display_filter = display_filter.get_filter_queryset()[start_index:]  
    
    
    #build json_string with information from data    
     
    json_string = "{ \"aaData\": ["
   
    #adding user
    for case in display_filter:
        careteam_url = reverse('view-careteam', kwargs={"careteam_id": case.careteam_set.get().id})
        json_string += "["
        json_string += "\"<a href = '%s'>%s</a>\"," % (careteam_url, case.careteam_set.get().patient.user.get_full_name())
        for col in filter.gridpreference.get_display_columns:
            table_entry = case_column(case, col.name)
            if len(table_entry) > 45:
                table_entry = table_entry[0:45] + "..."
            # terribly hardcoded...quick fix to add links
            if (col.name == "description"):
                json_string +=  "\"<a href = 'case/%s'>%s</a>\"," % (case.id, table_entry)
            else:
                json_string += "\"%s\"," % table_entry
        json_string += "],"
    
    #terribly inefficient, but quick fix to allow sorting of links....
#    json_string += " ], \"aoColumns\": [ null,"
#    for col in filter.gridpreference.display_columns.all():
#        json_string += "{\"sType\": \"html\"},"
    #closing json_string
    json_string += "] }"

    return HttpResponse(json_string)

@login_required
#@cache_page(60 * 5)
def my_dashboard_tab(request, template_name="ashandapp/filter_datatable.html"): 
 
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
    context['grid_name'] = "filter-%d" % profile.last_filter.id
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
    
    
    ########################
    #get the shared filters
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
    ############################
    
    
    
    #get the specific case querysets based upon the user logged in.
    context['user_grids'] = []
    
    #if a patient, get their careteam's cases
    if request.is_patient:
        pass
    
    #if a caregiver, get querysets for all the patients that they care for
    if request.is_caregiver:        
        context['user_grids'].append(('caregiver_cases', 'People I Care For', reverse('grid_caregiver_cases')))    
    
    if request.is_provider:
        #if a provider/nurse, get the inbound triage for all their patients
        #if a doctor, just get all cases for all their patients
        careteam_links = ProviderLink.objects.filter(provider=request.provider)    
        if careteam_links.count() > 0:            
            context['user_grids'].append(('patient_cases', 'My Patients', reverse('grid_provider_patient_cases')))
#            
#            triage_cases = careteam_links.filter(role__role='nurse-triage')
#                        
#            if triage_cases.count() > 0:
#                context['user_grids'].append(('triage_cases', 'Inbound Triage',['patient','description','opened_date','priority'],reverse('view-cases-for-triage-json')))
#        
        
    context['recent_activity_grid'] = [('recent_cases', 'Recent Activity', reverse('grid_recent_activity'))]
            
    return render_to_response(template_name, context, context_instance=RequestContext(request))
