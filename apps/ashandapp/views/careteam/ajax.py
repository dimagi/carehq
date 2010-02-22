import logging
from datetime import datetime


from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from casetracker.models import Case, Filter
from ashandapp.models import CaseProfile, CareTeam,ProviderLink
from provider.models import Provider
from patient.models import Patient
from django.db.models import Q
from django.views.decorators.cache import cache_page

from ashandapp.decorators import is_careteam_member

@login_required
@is_careteam_member
def view_careteam_cases(request, careteam_id, template_name="ashandapp/careteam/careteam_cases_ajax.html"):    
    context = {}
    careteam = CareTeam.objects.get(id=careteam_id)
    #cases = careteam.cases.all()
    
        
    #reverse('view-careteam', kwargs={"careteam_id": case.careteam_set.get().id})
    context['active_qset_url'] = reverse('careteam-cases-grid', kwargs = {"careteam_id":careteam.id}) + "?mode=active"
    context['resolved_qset_url'] = reverse('careteam-cases-grid', kwargs = {"careteam_id":careteam.id}) + "?mode=resolved"
    context['closed_qset_url'] = reverse('careteam-cases-grid', kwargs = {"careteam_id":careteam.id}) + "?mode=closed"
    context['all_qset_url'] = reverse('careteam-cases-grid', kwargs = {"careteam_id":careteam.id}) + "?mode=all"
    
    context['active_title'] = 'Active'
    context['resolved_title'] = 'Resolved'
    context['closed_title'] = 'Closed'
    context['all_title'] = 'All'
    
        
    #context['cases'] = cases    
    context['patient']= careteam.patient    
    context['careteam'] = careteam
    return render_to_response(template_name, context, context_instance=RequestContext(request))
