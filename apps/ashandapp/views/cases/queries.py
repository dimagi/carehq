import logging
from datetime import datetime

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from casetracker.queries.caseevents import get_latest_event, get_latest_for_cases
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from casetracker.models import Case, Filter, CaseEvent
from ashandapp.models import CaseProfile, CareTeam, ProviderLink
from provider.models import Provider
from patient.models import Patient
from careplan.models import CarePlan, CarePlanItem

from ashandapp.templatetags.filter_tags import case_column
from ashandapp.decorators import provider_only, caregiver_only, patient_only, is_careteam_member
from ashandapp.models import CareTeam, ProviderRole, ProviderLink, CaregiverLink, CareRelationship,CareTeamCaseLink
from django.db import connection

from casetracker import constants

#patient implicitly first
DEFAULT_COLUMNS = ['category', 'description','priority','assigned_to', 'next_action', 'next_action_date']


def do_get_json(cases_qset, columns):
    #build json_string with information from data    
    json_string = "{ \"aaData\": ["
   
    #adding user
    for case in cases_qset:
        #todo, this is pretty inefficient on db lookups since we're pulling the reverse of the careteam on each case
        careteam_url = reverse('view-careteam', kwargs={"careteam_id": case.careteam_set.get().id})
        json_string += "["
        json_string += "\"<a href = '%s'>%s</a>\"," % (careteam_url, case.careteam_set.get().patient.user.get_full_name())
        for col in columns:
            table_entry = case_column(case, col)
            if len(table_entry) > 80:
                table_entry = table_entry[0:80] + "..."
            # terribly hardcoded...quick fix to add links
            if (col == "description"):
                json_string +=  "\"<a href = '%s'>%s</a>\"," % (reverse('view-case', kwargs={'case_id':case.id }), table_entry)
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
def grid_recent_activity(request, template_name="ashandapp/cases/bare_query.html"):
    """
    Return a case queryset of all the patients that this caregiver is working on.        
    """
    context = {} 
    columns = ['description','status', 'last_case_event','last_event_date']       
    context['colsort_array'] = [[4,'asc']]   
    do_json=False
    if len(request.GET.items()) > 0:
        for item in request.GET.items():
            if item[0] == 'json':
                do_json=True    
    if do_json:
        last_activity_list = CaseEvent.objects.filter(created_by=request.user).values_list('case',flat=True)        
        cases = Case.objects.select_related('opened_by','last_edit_by',\
                                          'resolved_by','closed_by','assigned_to',
                                          'priority','category','status').filter(id__in=last_activity_list).distinct()
        assigned_cases = Case.objects.all().filter(assigned_to=request.user).distinct()
        
        return  do_get_json((cases | assigned_cases), columns)
    else:
        context['grid_name'] = 'grid_recents'
        context['json_qset_url'] = request.path + "?json"
        context['columns'] = columns
        return render_to_response(template_name, context, context_instance=RequestContext(request))


@login_required
#@provider_only
def grid_caregiver_cases(request, template_name="ashandapp/cases/bare_query.html"):
    """
    Return a case queryset of all the patients that this caregiver is working on.        
    """
    context = {} 
    columns = ['description','status', 'last_case_event','last_event_by', 'last_event_date']
    context['colsort_array'] = [[5,'desc']]          
    do_json=False
    if len(request.GET.items()) > 0:
        for item in request.GET.items():
            if item[0] == 'json':
                do_json=True    
    if do_json:        
        careteams = CaregiverLink.objects.all().filter(user = request.user).values_list('careteam__id', flat=True)
        careteam_cases = CareTeamCaseLink.objects.all().filter(careteam__in=careteams).values_list('case__id', flat=True)
        qset= Case.objects.all().select_related('opened_by','last_edit_by',\
                                          'resolved_by','closed_by','assigned_to',
                                          'priority','category','status').filter(id__in=careteam_cases)         
        return  do_get_json(qset, columns)
    else:
        context['grid_name'] = 'grid_caregiver_cases'
        context['json_qset_url'] = request.path + "?json"
        context['columns'] = columns
        return render_to_response(template_name, context, context_instance=RequestContext(request))


def _get_careteam_triage_qset(careteam):
    """
    return a queryset of cases that fit the triage criteria
    NEW
    or 
    UNASSIGNED
    
    Callers:
    for a triage nurse, ie, if you are multiple primary_providers for mulitple careteams
    this should be called multiple times and merged.
    
    but this is the low level query for a single careteam.
    """

    newstate_q = Q(status__state_class=constants.CASE_STATE_NEW)
    no_assignment_q = Q(assigned_to=None)
    
    qset= careteam.all_cases().filter(newstate_q | no_assignment_q)
    return qset


@login_required
@provider_only
def grid_triage_cases(request, template_name="ashandapp/cases/bare_query.html"):
    """
    For a given provider, return all the cases merged for whom they triage
    """
    context = {}
    columns = ['opened_by', 'description','opened_date',]
    context['colsort_array'] = [[2,'desc']]
    do_json=False
    if len(request.GET.items()) > 0:
        for item in request.GET.items():
            if item[0] == 'json':
                do_json=True    
    if do_json:
        careteam_links = ProviderLink.objects.filter(provider=request.provider)    
        as_primary = careteam_links.filter(role__role='nurse-triage').values_list('careteam', flat=True)        
        careteam_cases = CareTeamCaseLink.objects.all().filter(careteam__in=as_primary).values_list('case__id', flat=True)      
        qset= Case.objects.select_related('opened_by','last_edit_by',\
                                          'resolved_by','closed_by','assigned_to',
                                          'priority','category','status').filter(id__in=careteam_cases)        
        qset = qset.filter(status__state_class=constants.CASE_STATE_NEW)
        
        return do_get_json(qset, columns)    
    else:               
        context['grid_name'] = 'grid_triage_cases'
        context['json_qset_url'] = request.path + "?json"
        context['columns'] = columns
        return render_to_response(template_name, context, context_instance=RequestContext(request))




@login_required
@provider_only
def grid_provider_patient_cases(request, template_name="ashandapp/cases/bare_query.html"):
    """
    For a given doctor, this is a huge query to get all the cases for all their patients    
    """      

    do_json=False
    if len(request.GET.items()) > 0:
        for item in request.GET.items():
            if item[0] == 'json':
                do_json=True    
    context = {}        
    columns = ['assigned_to','description','last_event_by', 'last_event_date', 'next_action_date']
    context['colsort_array'] = [[5,'desc']]
    if do_json:
        from django.db import connection
        connection.queries = []
        careteam_links = ProviderLink.objects.select_related().filter(provider=request.provider).values_list('careteam__id',flat=True)        
        caselink_ids = CareTeamCaseLink.objects.select_related().filter(careteam__in=careteam_links).values_list('case__id',flat=True)
        qset = Case.objects.select_related('opened_by','last_edit_by',\
                                          'resolved_by','closed_by','assigned_to',
                                          'priority','category','status').filter(id__in=caselink_ids).exclude(next_action_date=None)                        
        ret = do_get_json(qset, columns)
#        sql = [x['sql'] for x in connection.queries]
#        fout = open('/home/dmyung/provider-sql','w')
#        for s in sql:
#            fout.write(s + "\n")
#        fout.close()
        
        return ret    
    else:
        context['grid_name'] = 'grid_provider_patient_cases'
        context['json_qset_url'] = request.path + "?json" 
        
        context['columns'] = columns
        return render_to_response(template_name, context, context_instance=RequestContext(request))



@login_required
def grid_careteam_cases(request, careteam_id, template_name="ashandapp/cases/bare_query.html"):
    """
    Return a case queryset of all the patients that this caregiver is working on.        
    """
    context = {} 
    columns = ['description','status', 'last_case_event','last_event_by', 'last_event_date']
    context['colsort_array'] = [[5,'desc']]          
    do_json=False
    viewmode = 'all'
    careteam = CareTeam.objects.get(id=careteam_id)
    if len(request.GET.items()) > 0:
        for item in request.GET.items():
            if item[0] == 'json':
                do_json=True    
            elif item[0] == 'mode':
                viewmode = item[1]
    
    
    if viewmode == 'active':
        columns = ['category', 'description', 'assigned_to', 'next_action', 'next_action_date']
        context['colsort_array'] = [[5,'asc']]
    elif viewmode == 'resolved':
        columns = ['category', 'description', 'resolved_by', 'resolved_date']
        context['colsort_array'] = [[4,'desc']]
    elif viewmode == 'closed':
        columns = ['category', 'description','closed_by', 'closed_date']
        context['colsort_array'] = [[4,'desc']]
    elif viewmode == 'all':
        columns = ['category', 'description', 'assigned_to', 'status', 'last_case_event', 'last_event_date']
        context['colsort_array'] = [[6,'desc']]    
    
    if do_json:        
        if viewmode == 'active':
            qset = careteam.active_cases()
        elif viewmode == 'resolved':
            qset = careteam.resolved_cases()
        elif viewmode == 'closed':
            qset = careteam.closed_cases()
        elif viewmode == 'all':
            qset = careteam.all_cases()
        return  do_get_json(qset, columns)
    else:
        context['grid_name'] = 'grid_caregiver_cases'
        context['json_qset_url'] = request.path + "?mode=%s&json" % viewmode
        context['columns'] = columns
        return render_to_response(template_name, context, context_instance=RequestContext(request))



@login_required
def grid_cases_for_object(request, content_type_name=None, content_uuid=None, template_name="ashandapp/cases/query_test.html"):
    context = {} 
    ctype = ContentType.objects.all().get(model=content_type_name)
    obj = ctype.model_class().objects.get(id=content_uuid)     
    do_json=False
    if len(request.GET.items()) > 0:
        for item in request.GET.items():
            if item[0] == 'json':
                do_json=True    
            if item[0] == 'filter':
                filter_id = item[1]    
            if item[0] == 'iDisplayStart':
                start_index = item[1]
    
    if do_json:
        user = request.user          
        if isinstance(obj, CareTeam):
            cases_qset = obj.all_cases()
        elif isinstance(obj, Provider):
            cases_qset = Case.objects.all().filter(assigned_to=obj.user)
        elif isinstance(obj, Patient):
            careteam = CareTeam.objects.get(patient=obj)
            cases_qset = careteam.all_cases()
        elif isinstance(obj, User):
            cases_qset = Case.objects.all().filter(assigned_to=obj)
        elif isinstance(obj, CarePlan):
            cases_qset = obj.cases.all()
        elif isinstance(obj, CarePlanItem):
            pass    
        return do_get_json(cases_qset, DEFAULT_COLUMNS)
    else:        
        context['obj'] = obj
        context['obj_type'] = content_type_name    
        
        context['columns'] = DEFAULT_COLUMNS
        return render_to_response(template_name, context, context_instance=RequestContext(request))
    
