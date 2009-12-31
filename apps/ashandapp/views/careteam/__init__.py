from django.shortcuts import render_to_response

from django.contrib.auth.decorators import login_required
from django.template import RequestContext
import logging
from django.contrib.auth.models import User
from casetracker.models import Case, Filter
from ashandapp.models import CaseProfile, CareTeam,ProviderLink
from provider.models import Provider
from patient.models import Patient
from casetracker.datagrids import CaseDataGrid, CaseEventDataGrid, FilterDataGrid
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from casetracker.queries.caseevents import get_latest_event, get_latest_for_cases

from ashandapp.forms.inquiry import NewInquiryForm
from ashandapp.forms.issue import NewIssueForm


def single(request, careteam_id, template_name="ashandapp/view_careteam.html"):    
    context = {}
    careteam = CareTeam.objects.get(id=careteam_id)
    #careteam.
    
    context['careteam'] = careteam
                
    cases = careteam.cases.all()
    context['cases'] = cases
    #cases_datagrid = CaseDataGrid(request, qset=cases,qtitle="Cases for careteam")
    #context['cases_datagrid'] = cases_datagrid
    context['patient']= Patient.objects.get(user=careteam.patient)
    
    provider_links_raw = careteam.providerlink_set.all()
    provider_dict = {}
    
    for plink in provider_links_raw:
        puser = plink.provider
        prov = Provider.objects.filter(user=puser).select_related('user')
        provider_dict[prov[0]] = plink
    context['provider_dict'] = provider_dict
    
    return render_to_response(template_name, context, context_instance=RequestContext(request))
