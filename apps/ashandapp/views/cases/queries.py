from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from casetracker.models import Case, Filter, CaseEvent
from patient.models import Patient
from careplan.models import CarePlan, CarePlanItem

from ashandapp.templatetags.filter_tags import render_case_column
from ashandapp.models import CareTeam, ProviderLink, CaregiverLink, CareTeamCaseLink


from casetracker import constants
import json 

#patient implicitly first
DEFAULT_COLUMNS = ['category', 'description','priority','assigned_to']


def do_get_patient_case_json(cases_qset, columns, request):
    #build json_string with information from data    
    context = {}    
    output = {'aaData':[]}
    for case in cases_qset:
        row_arr = []
        for col in columns:
            table_entry = render_case_column(case, col, plain_text=False)
            row_arr.append(table_entry)
        output['aaData'].append(row_arr)
    context['json_string'] = json.dumps(output)    
    
#    json_string = "{ \"aaData\": ["
#   
#    #adding user
#    for case in cases_qset:
#        #todo, this is pretty inefficient on db lookups since we're pulling the reverse of the careteam on each case
#        careteam_url = reverse('view-careteam', kwargs={"careteam_id": case.careteam_set.get().id})
#        json_string += "["
#        #json_string += "\"<a href = '%s'>%s</a>\"," % (careteam_url, case.careteam_set.get().patient.user.title())
#        for col in columns:
#            table_entry = case_column(case, col)
#            if len(table_entry) > 80:
#                table_entry = table_entry[0:80] + "..."
#            # terribly hardcoded...quick fix to add links
#            if (col == "description"):
#                json_string +=  "\"<a href = '%s'>%s</a>\"," % (reverse('manage-case', kwargs={'case_id':case.id }), table_entry)
#            else:
#                json_string += "\"%s\"," % table_entry
#        json_string += "],"
#    
    #terribly inefficient, but quick fix to allow sorting of links....
#    json_string += " ], \"aoColumns\": [ null,"
#    for col in filter.gridpreference.display_columns.all():
#        json_string += "{\"sType\": \"html\"},"
    #closing json_string
    #json_string += "] }"
    
    #context['json_string'] = json_string
    if request.GET.has_key('debug'):
        template = 'carehqapp/json_debug.html'
    else:
        template = 'carehqapp/json.html'
    return render_to_response(template, context, context_instance=RequestContext(request))
    #return HttpResponse(json_string)
    

@login_required
def grid_recent_activity(request, template_name="carehqapp/cases/bare_query.html"):
    """
    Return a case queryset of all the patients that this caregiver is working on.        
    """
    context = {} 
    columns = ['patient', 'description','status', 'last_case_event','last_event_date']       
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
        
        return  do_get_patient_case_json((cases | assigned_cases), columns, request)
    else:
        context['grid_name'] = 'grid_recents'
        context['json_qset_url'] = request.path + "?json"
        context['columns'] = columns
        context['column_stype_json'] = get_column_types(columns)
        return render_to_response(template_name, context, context_instance=RequestContext(request))


@login_required
#@provider_only
def grid_caregiver_cases(request, template_name="carehqapp/cases/bare_query.html"):
    """
    Return a case queryset of all the patients that this caregiver is working on.        
    """
    context = {} 
    columns = ['patient', 'description','status', 'last_case_event','last_event_by', 'last_event_date']
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
        return  do_get_patient_case_json(qset, columns, request)
    else:
        context['grid_name'] = 'grid_caregiver_cases'
        context['json_qset_url'] = request.path + "?json"
        context['columns'] = columns
        context['column_stype_json'] = []
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

    newstate_q = Q(status__state_class=constants.CASE_STATE_OPEN) #changed from CASE_STATE_NEW.  this should be a CASE_STATE_OPEN with a where on the "triage" status
    no_assignment_q = Q(assigned_to=None)
    
    qset= careteam.all_cases().filter(newstate_q | no_assignment_q)
    return qset


@login_required
@provider_only
def grid_triage_cases(request, template_name="carehqapp/cases/bare_query.html"):
    """
    For a given provider, return all the cases merged for whom they triage
    """
    context = {}
    columns = ['patient', 'opened_by', 'description','opened_date',]
    context['colsort_array'] = [[3,'desc']]
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
        qset = qset.filter(status__state_class=constants.CASE_STATE_OPEN) #changed from CASE_STATE_NEW.  this should be a CASE_STATE_OPEN with a where on the "triage" status
        
        return do_get_patient_case_json(qset, columns, request)    
    else:               
        context['grid_name'] = 'grid_triage_cases'
        context['json_qset_url'] = request.path + "?json"
        context['columns'] = columns
        context['column_stype_json'] = get_column_types(columns)
        return render_to_response(template_name, context, context_instance=RequestContext(request))




@login_required
@provider_only
def grid_provider_patient_cases(request, template_name="carehqapp/cases/bare_query.html"):
    """
    For a given doctor, this is a huge query to get all the cases for all their patients    
    """      

    do_json=False
    if len(request.GET.items()) > 0:
        for item in request.GET.items():
            if item[0] == 'json':
                do_json=True    
    context = {}        
    columns = ['patient', 'assigned_to','description','last_event_by', 'last_event_date']
    context['colsort_array'] = [[5,'desc']]
    if do_json:
        from django.db import connection
        connection.queries = []
        careteam_links = ProviderLink.objects.select_related().filter(provider=request.provider).values_list('careteam__id',flat=True)        
        caselink_ids = CareTeamCaseLink.objects.select_related().filter(careteam__in=careteam_links).values_list('case__id',flat=True)
        qset = Case.objects.select_related('opened_by','last_edit_by',\
                                          'resolved_by','closed_by','assigned_to',
                                          'priority','category','status').filter(id__in=caselink_ids)
        ret = do_get_patient_case_json(qset, columns, request)
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
        context['column_stype_json'] = get_column_types(columns)
        return render_to_response(template_name, context, context_instance=RequestContext(request))



@login_required
def grid_careteam_cases(request, careteam_id, template_name="carehqapp/cases/bare_query.html"):
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
        columns = ['category', 'description', 'assigned_to','last_edit"date']
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
        return  do_get_patient_case_json(qset, columns, request)
    else:
        context['grid_name'] = 'grid_caregiver_cases'
        context['json_qset_url'] = request.path + "?mode=%s&json" % viewmode
        context['columns'] = columns
        context['column_stype_json'] = get_column_types(columns)
        return render_to_response(template_name, context, context_instance=RequestContext(request))



@login_required
def grid_cases_for_object(request, content_type_name=None, content_uuid=None, template_name="carehqapp/cases/query_test.html"):
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
        columns = DEFAULT_COLUMNS
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
        elif isinstance(obj, Filter):
            cases_qset = obj.get_filter_queryset()
            columns = obj.gridpreference.get_display_columns
            
        return do_get_patient_case_json(cases_qset, columns, request)
    else:        
        context['obj'] = obj
        context['obj_type'] = content_type_name    
        
        context['columns'] = DEFAULT_COLUMNS
        context['column_stype_json'] = get_column_types(DEFAULT_COLUMNS)
        return render_to_response(template_name, context, context_instance=RequestContext(request))
    
