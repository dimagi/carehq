from datetime import datetime
import logging

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse
from casetracker.models import Filter, Case, CaseEvent, Status, Category, Priority
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from provider.models import Provider
from ashandapp.models import CareTeam, ProviderRole, ProviderLink, CaregiverLink, CareRelationship, FilterProfile
from django.db.models import Q


from ashandapp.forms.question import NewQuestionForm
from ashandapp.forms.issue import NewIssueForm
from ashandapp.templatetags.filter_tags import case_column_plain
from ashandapp.views.cases import queries

def process_filter_change(request):
    """
    From the main toolbar, case filters will be changed/chosen from the pulldown.
    The POST will put put the filter/query ID into the request, and put a POST in here.
    then, the viewprofile object will update with the case filter for them to see when they click back on the "case list"  
    """
    pass


@login_required
def list_cases(request, template_name="ashandapp/list_cases.html"):
    context = {}
    user = request.user    
    
    ########################
    #get the logged in user's filter profile, if the profile doesn't exist, make a new FilterProfile and arbitrarily use the first case filter
    # if it does exist, load up the last filter used, OR whatever the query string is saying it is.
    display_filter = None    
    
    request.session['is_listing'] = 'something'
    request.session['is_whatever'] = 'askldjqwoerwqer'
    request.session.modified=True
    try:
        profile = FilterProfile.objects.get(user = user)                    
    except ObjectDoesNotExist:
        #make the new case profile
        profile = FilterProfile()
        profile.user = user
        profile.filter = Filter.objects.all()[0]
        profile.last_filter = Filter.objects.all()[0] #this is a nasty hack, as we're assuming id 1 is the reflexive one 

    display_filter = profile.last_filter    
    
    
    group_by_col = None
    if len(request.GET.items()) > 0:
            for item in request.GET.items():
                if item[0] == 'filter':
                    filter_id = item[1]            
                    try:
                        display_filter = Filter.objects.get(id=filter_id)                                                
                    except:
                        pass
                if item[0] == "groupBy":
                    group_by_col = item[1]
            
    profile.last_login = datetime.utcnow()
    profile.last_login_from = request.META['REMOTE_ADDR']
    profile.last_filter = display_filter
    profile.save()

    split_headings = False
    qset = display_filter.get_filter_queryset()    
    
    
    if group_by_col and group_by_col.count('_date') > 0:
        split_headings = False
        qset.order_by(group_by_col)
    elif group_by_col == 'description':
        split_headings = False
        qset.order_by('description')
    elif  group_by_col == 'assigned_to' or group_by_col == 'closed_by' or group_by_col == 'opened_by'\
        or group_by_col == 'last_edit_by' or group_by_col == 'resolved_by' or group_by_col == 'last_event_by':        
        model_class = User
        split_headings = True
    elif group_by_col == 'patient':        
        model_class = CareTeam
        split_headings = True
    elif group_by_col == 'status':
        model_class = Status
        split_headings = True
    elif group_by_col == 'priority':
        model_class = Priority
        split_headings = True
    elif group_by_col == 'category':
        model_class = Category
        split_headings = True
    
    qset_dict = {}
    
    #If we are splitting the queryset up by the sorting category,
    #we need to iterate over the distinct objects in the model class
    if split_headings:
        heading_keys = model_class.objects.all().distinct() #This is a bit inefficient as it does it over all the 
        for key in heading_keys:            
            #http://www.nomadjourney.com/2009/04/dynamic-django-queries-with-kwargs/
            #dynamic django queries baby
            if group_by_col == 'patient':
                ptq = Q(careteam=key)
                subq = qset.filter(ptq)
            else:
                kwargs = {str(group_by_col +"__id__endswith"): str(key.id), }
                subq = qset.filter(**kwargs)        
            if subq.count() > 0:
                qset_dict[key] = subq
    else:
        qset_dict[display_filter.description] = display_filter.get_filter_queryset()
        
    
    context['qset_dict'] = qset_dict
    context['profile'] = profile    
    context['filter'] = display_filter
    context['filter_cases'] = display_filter.get_filter_queryset()    
    context['gridpreference'] = context['filter'].gridpreference
    ############################
    
    filter_columns = display_filter.gridpreference.get_display_columns.values_list('column__name', flat=True)
    context['columns'] = display_filter.gridpreference.get_display_columns
    
    
    return render_to_response(template_name, context, context_instance=RequestContext(request))
