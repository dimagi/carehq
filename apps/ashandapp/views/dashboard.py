from datetime import datetime

from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse
from casetracker.models import Filter, Category, Status, Priority
from django.db.models import Q

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from ashandapp.models import FilterProfile

from ashandapp.templatetags.filter_tags import case_column_plain
from patient.models.djangomodels import Patient


@login_required
def get_json_for_paging(request):    
    user = request.user    
    display_filter = None    
    start_index = None
    length = None

    try:
        profile = FilterProfile.objects.get(user = user)                
    except ObjectDoesNotExist:
        #make the new case profile
        profile = FilterProfile()
        profile.user = user
        profile.filter = Filter.objects.all()[0]
        profile.last_filter = Filter.objects.all()[0] #this is a nasty hack, as we're assuming id 1 is the reflexive one 
    
    
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
        json_string += "\"<a href = '%s'>%s</a>\"," % (careteam_url, case.careteam_set.get().patient.user.title())
        for col in filter.gridpreference.get_display_columns:
            table_entry = case_column_plain(case, col.name)
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


def dashboard_case_filter(request, filter_id):
    context = {}
    showfilter = False        
    filter = Filter.objects.get(id=filter_id)
    gridpref = filter.gridpreference    
    group_by = None    
        
    for key, value in request.GET.items():            
        if key == "groupBy":
            group_by_col = value
    
    split_headings = True
    qset = filter.get_filter_queryset()    
        
    if group_by_col.count('_date') > 0:
        split_headings = False
        qset.order_by(group_by_col)
    elif group_by_col == 'description':
        split_headings = False
        qset.order_by('description')
    elif  group_by_col == 'assigned_to' or group_by_col == 'closed_by' or group_by_col == 'opened_by'\
        or group_by_col == 'last_edit_by' or group_by_col == 'resolved_by' or group_by_col == 'last_event_by':        
        model_class = User
    elif group_by_col == 'patient':        
        model_class = Patient
    elif group_by_col == 'status':
        model_class = Status
    elif group_by_col == 'priority':
        model_class = Priority
    elif group_by_col == 'category':
        model_class = Category
    
    qset_dict = {}
    
    if split_headings:
        heading_keys = model_class.objects.all().distinct()
        for key in heading_keys:
            #http://www.nomadjourney.com/2009/04/dynamic-django-queries-with-kwargs/
            #dynamic django queries baby
            #kwargs = { 'deleted_datetime__isnull': True }
            #args = ( Q( title__icontains = 'Foo' ) | Q( title__icontains = 'Bar' ) )
            #entries = Entry.objects.filter( *args, **kwargs )
            if group_by_col == 'patient':
                ptq = Q(patient=key)
                subq = qset.filter(ptq)
            else:
                kwargs = {str(group_by_col): key, }
                subq = qset.filter(**kwargs)        
    else:
        pass

    
    context['filter'] = filter
    context['gridpref'] = gridpref
    
        
    context['filter_cases'] = qset
    template_name='casetracker/filter/filter_simpletable.html'
    return render_to_response(template_name, context, context_instance=RequestContext(request))


        



@login_required
def view_caselist_fbstyle(request, filter_id):
    context = {}
    for key, value in request.GET.items():            
        if key == "sort":
            sorting = value

