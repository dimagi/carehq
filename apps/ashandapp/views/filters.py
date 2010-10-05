from datetime import datetime

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from casetracker.models import Filter, Status, Category, Priority
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from ashandapp.models import FilterProfile
from django.db.models import Q
from patient.models.djangomodels import Patient


def process_filter_change(request):
    """
    From the main toolbar, case filters will be changed/chosen from the pulldown.
    The POST will put put the filter/query ID into the request, and put a POST in here.
    then, the viewprofile object will update with the case filter for them to see when they click back on the "case list"  
    """
    pass

def filter_cases_for_user(qset, user):
    if user.is_superuser:
        return qset
    providers = Provider.objects.filter(user=user)
    patient = user.patient_user.only()
#    careteams = CareTeam.objects.filter( Q(caregivers=user) | Q(providers=providers) | Q(patient=patient) )
#    return qset.filter(careteam=careteams)
    raise Exception("filter_cases_for_user, not implementing new actor model yet")

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

    if 'filter' in request.GET:
        filter_id = request.GET['filter']
        display_filter = Filter.objects.get(id=filter_id)
    else:
        display_filter = profile.last_filter
    group_by_col = request.GET.get('groupBy', None)

            
    profile.last_login = datetime.utcnow()
    profile.last_login_from = request.META['REMOTE_ADDR']
    profile.last_filter = display_filter
    profile.save()

    split_headings = False
    qset = display_filter.get_filter_queryset()    
    
    qset = filter_cases_for_user(qset, user)
    
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
        model_class = Patient
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
                subq = qset.filter(careteam=key)
            else:
                kwargs = {str(group_by_col +"__id__endswith"): str(key.id), }
                subq = qset.filter(**kwargs)
            if subq.count() > 0:
                qset_dict[key] = subq
    else:
        qset_dict[display_filter.description] = qset
        
    
    context['qset_dict'] = qset_dict
    context['profile'] = profile    
    context['filter'] = display_filter
    #context['filter_cases'] = display_filter.get_filter_queryset()    
    context['gridpreference'] = context['filter'].gridpreference
    ############################
    
    filter_columns = display_filter.gridpreference.get_display_columns.values_list('column__name', flat=True)
    context['columns'] = display_filter.gridpreference.get_display_columns
    
    
    return render_to_response(template_name, context, context_instance=RequestContext(request))
