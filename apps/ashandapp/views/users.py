from django.shortcuts import render_to_response
from ashandapp.datagrids import UserDataGrid
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
import logging
from django.contrib.auth.models import User
from casetracker.models import Case, Filter
from ashandapp.models import CaseProfile, CareTeam, ProviderLink, CaregiverLink
from provider.models import Provider
from patient.models import Patient
from casetracker.datagrids import CaseDataGrid, CaseEventDataGrid, FilterDataGrid
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from casetracker.queries.caseevents import get_latest_event, get_latest_for_cases

from ashandapp.forms.question import NewQuestionForm
from ashandapp.forms.issue import NewIssueForm
from casetracker.views import get_sorted_dictionary 
 

@cache_page(60 * 5)
def all(request, template_name='ashandapp/user_datagrid.html'):
    return UserDataGrid(request).render_to_response(template_name)


def my_profile(request, template_name = 'ashandapp/my_profile.html'):
    user = request.user
    context = {}        
    return render_to_response(template_name, context, context_instance=RequestContext(request))


#@cache_page(60 * 5)
@login_required
def single(request, user_id=None):
    context = {}
    if user_id==None:
        user = request.user
    else:
        user = User.objects.get(id=user_id)
    
    sort = None
    
    try:
        for key, value in request.GET.items():
            if key == "sort":
                sort = value
    except:
        sort = None
    
    context['selected_user'] = user
    
    #establish patient information
    
    #=======================================
    #Section to determine request.user's relationship with selected user beinga patient        
    try:
        template_name = "ashandapp/view_patient.html"
        patient = Patient.objects.all().get(user=user)
        context['selected_is_patient'] = True
        context['selected_patient'] = patient
    except:
        template_name = "ashandapp/view_user.html"
        context['selected_is_patient'] = False
    
    if context['selected_is_patient']:        
        careteam = CareTeam.objects.get(patient=user)
        context['selected_careteam'] = careteam
        
        #now see what the request.user's relationship is to the patient
        context['is_provider_for'] = False
        if request.is_provider:
            if ProviderLink.objects.filter(careteam=careteam).filter(provider = request.provider).count() > 0:                
                context['is_provider_for'] = True
                
        try:                            
            context['caregiver_role'] = CaregiverLink.objects.filter(careteam=careteam).get(user=request.user)
            context['is_caregiver_for'] = True
        except:
            context['is_caregiver_for'] = False
    
    
    
        if context['is_provider_for'] or context['is_caregiver_for']:            
            context['events'] = get_latest_for_cases(context['selected_careteam'].cases.all())
            context['formatting'] = False     
        
            sorted_dic = {}
            sorted_dic = get_sorted_dictionary(sort, context['events'])
                        
            if (len(sorted_dic) > 0):
                context['events'] = sorted_dic
                context['formatting'] = True
                              
            cases = CareTeam.objects.get(patient=user).cases.all()  
            context['cases'] = cases    

    
    
    #=======================================
    #Section to determine request.user's relationship with selected user being provider
    try:
        selected_provider = Provider.objects.get(user=user)
        selected_is_provider=True
        context['selected_provider'] = selected_provider
    except ObjectDoesNotExist:
        selected_is_provider=False
        
    
    context['selected_is_provider'] = selected_is_provider
    if selected_is_provider:
        #ok, so they are a provider, now let's see if we are on the same care team anywhere        
        template_name = "ashandapp/view_provider.html"
        
        #careteams that the provider is a part of
        plink_selected = ProviderLink.objects.all().filter(provider=selected_provider)
        
        
        #find common careteams - first, get the careteams i am a part of
        if request.is_provider:
            careteams_me = ProviderLink.objects.all().filter(provider=request.provider).values_list('careteam', flat=True)                 
        elif request.is_caregiver:
            careteams_me = CaregiverLink.objects.all().filter(user=request.user).values_list('careteam', flat=True)
        
        common_careteam_ids = plink_selected.filter(careteam__in=careteams_me).values_list('careteam',flat=True)
        context['common_careteams'] = CareTeam.objects.filter(id__in=common_careteam_ids)
        
#        #if a provider, do the provider queries        
#        opened = Q(opened_by=user)
#        last_edit = Q(last_edit_by=user)
#        assigned = Q(assigned_to=user)
#        
#        cases = Case.objects.select_related('opened_by','last_edit_by','status').filter(opened | last_edit | assigned)
#        context['cases'] = cases
        
        
    #todo: if selected_is_caregiver?
    
         
    return render_to_response(template_name, context, context_instance=RequestContext(request))

