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

from casetracker.models import Case, Filter
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
        json_string += "["
        json_string += "\"<a href = 'users/%s'>%s %s</a>\"," % (case.careteam_set.get().patient.user.id, case.careteam_set.get().patient.user.first_name, case.careteam_set.get().patient.user.last_name)
        for col in columns:
            table_entry = case_column(case, col)
            if len(table_entry) > 45:
                table_entry = table_entry[0:45] + "..."
            # terribly hardcoded...quick fix to add links
            if (col == "description"):
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
#@provider_only
def view_json_caregiver_cases(request, template_name="ashandapp/cases/bare_query.html"):
    context = {}        
    context['json_qset_url'] = reverse('cases-for-caregiver-json')
    context['columns'] = ['description','status','last_case_event','last_event_by', 'last_event_date']
    return render_to_response(template_name, context, context_instance=RequestContext(request))


@login_required
#@caregiver_only
def json_caregiver_cases(request):
    """
    Return a case queryset 3-tuple of all the patients that this caregiver is working on.
    
    return a 3-tuple of (tabdisplay, columns, queryset)    
    """
    #print 'json_caregiver_cases'
    careteams = CaregiverLink.objects.all().filter(user = request.user).values_list('careteam__id', flat=True)
    careteam_cases = CareTeamCaseLink.objects.all().filter(careteam__in=careteams).values_list('case__id', flat=True)
    qset= Case.objects.all().filter(id__in=careteam_cases)
    #print qset
    columns = ['description','status', 'last_case_event','last_event_by', 'last_event_date']    
    return  do_get_json(qset, columns)
    
    

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
#@provider_only
def view_json_triage_cases(request, template_name="ashandapp/cases/bare_query.html"):
    context = {}        
    context['json_qset_url'] = reverse('cases-for-triage-json')
    context['columns'] = ['description','opened_date','priority']
    return render_to_response(template_name, context, context_instance=RequestContext(request))


@login_required
@provider_only
def json_triage_cases(request):
    """
    For a given provider, return all the cases merged for whom they triage
    """
    careteam_links = ProviderLink.objects.filter(provider=request.provider)    
    as_primary = careteam_links.filter(role__role='nurse-triage')
    
    curr_qset = None
    to_return = None
    for link in careteam_links:
        qset = _get_careteam_triage_qset(link.careteam)
        if to_return==None:
            to_return = qset
        else:
            to_return = to_return | qset
    
    columns = ['description','opened_date','priority']
    return do_get_json(to_return, columns)    



@login_required
@provider_only
def view_json_provider_patient_cases(request, template_name="ashandapp/cases/bare_query.html"):
    context = {}        
    context['json_qset_url'] = reverse('cases-for-provider-json')
    context['columns'] = ['description','assigned_to','last_event_by', 'last_event_date', 'next_action_date']
    return render_to_response(template_name, context, context_instance=RequestContext(request))

@login_required
@provider_only
def json_provider_patient_cases(request):
    """
    For a given doctor, this is a huge query to get all the cases for all their patients    
    """    
    careteam_links = ProviderLink.objects.filter(provider=request.provider)   
    
    curr_qset = None
    to_return = None
    for link in careteam_links:
        qset = link.careteam.cases.all()
        if to_return==None:
            to_return = qset
        else:
            to_return = to_return | qset
#    if to_return:    
#        return ("Patient Triage", ['patient','description','assigned_to','last_event_by', 'last_event_date', 'next_action_date'], to_return)    
#    else:
#        return None    

    columns = ['description','assigned_to','last_event_by', 'last_event_date', 'next_action_date']
    return do_get_json(to_return, columns)
        





@login_required
def get_cases_for_obj_json(request, content_type_name=None, content_uuid =None):
    
    user = request.user
    
    ctype = ContentType.objects.all().get(model=content_type_name)
    obj = ctype.model_class().objects.get(id=content_uuid)
    
    
    if len(request.GET.items()) > 0:
        for item in request.GET.items():
            if item[0] == 'filter':
                filter_id = item[1]    
            if item[0] == 'iDisplayStart':
                start_index = item[1]

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
#        qset_arr = []
#        for cp_item in obj.plan_items.all():            
#            qset_arr.append(cp_item.cases.all())
#todo recurse through all the items and get cases
        
        pass    
    return do_get_json(cases_qset, DEFAULT_COLUMNS)



@login_required
def view_cases_for_object(request, content_type_name=None, content_uuid=None, template_name="ashandapp/cases/query_test.html"):
    context = {}    
    ctype = ContentType.objects.all().get(model=content_type_name)
    obj = ctype.model_class().objects.get(id=content_uuid)
    context['obj'] = obj
    context['obj_type'] = content_type_name    
    
    context['columns'] = DEFAULT_COLUMNS
    return render_to_response(template_name, context, context_instance=RequestContext(request))
    
