from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
import logging
from django.contrib.auth.models import User
from casetracker.models import Case, Filter
from ashandapp.models import CaseProfile, CareTeam,ProviderLink
from provider.models import Provider
from patient.models import Patient

from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from casetracker.queries.caseevents import get_latest_event, get_latest_for_cases

from ashandapp.forms.inquiry import NewInquiryForm
from ashandapp.forms.issue import NewIssueForm


@login_required
def my_network(request, template_name='ashandapp/care_network.html'):
    #if i'm a patient, get my careteam and show providers    
    context = {}
    user = request.user    
    is_patient=False
    is_provider=False
    try:
        careteam = CareTeam.objects.get(patient=user)
        is_patient=True      
        context['my_careteam'] = careteam          
    except:                
        pass
    
    #if i'm a provider, get my patients and show them
    providers = Provider.objects.select_related('user').filter(user=request.user)
    if len(providers) > 0:
        is_provider = True
        #care_team_membership = ProviderLink.objects.select_related('care_team','provider','role').filter(provider__id=user.id).values_list("care_team__id",flat=True)
        care_team_members = ProviderLink.objects.filter(provider__id=user.id)
        care_team_membership = []
        for ct in care_team_members:
            care_team_membership.append(ct.id)
        context['my_patients_careteams'] = CareTeam.objects.filter(id__in=care_team_membership)    
    
    context['is_patient'] = is_patient
    context['is_provider'] = is_provider
    return render_to_response(template_name, context, context_instance=RequestContext(request))
