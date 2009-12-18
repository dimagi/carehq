from django.shortcuts import render_to_response
from datagrids import UserDataGrid
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from django.contrib.auth.models import User
from casetracker.models import Case
from models import CaseProfile, CareTeam,ProviderLink
from provider.models import Provider
from patient.models import Patient
from casetracker.datagrids import CaseDataGrid, CaseEventDataGrid, FilterDataGrid
from django.db.models import Q
 
def datagrids(request, template_name='ashandapp/datagrids.html'):
    return UserDataGrid(request).render_to_response(template_name)

def all_users(request, template_name='ashandapp/user_datagrid.html'):
    return UserDataGrid(request).render_to_response(template_name)


def styleguide(request, template_name="ashandapp/styleguide.html"):
    context = {}
    return render_to_response(template_name, context)


def view_user(request, user_id):
    context = {}
    user = User.objects.get(id=user_id)
    context['selected_user'] = user
    try:
        template_name = "ashandapp/view_patient.html"
        patient = Patient.objects.all().get(user=user)
        context['is_patient'] = True
        context['patient'] = patient
        context['careteam'] = CareTeam.objects.get(patient=user)
        cases = CareTeam.objects.get(patient=user).cases.all()
        print len(cases)
        qtitle = "Cases for this patient"
    except:
        template_name = "ashandapp/view_user.html"
        context['is_patient'] = False
    
    
    providers = Provider.objects.all().filter(user=user)
    if len(providers) > 0:
        context['providers'] = providers
        template_name = "ashandapp/view_provider.html"
        
        #if a provider, do the provider queries        
        opened = Q(opened_by=user)
        last_edit = Q(last_edit_by=user)
        assigned = Q(assigned_to=user)
        
        cases = Case.objects.filter(opened | last_edit | assigned)
        qtitle = "Cases for this provider"        
        care_team_membership = ProviderLink.objects.filter(provider__id=user.id).values_list("care_team__id",flat=True)
        context['care_teams'] = CareTeam.objects.filter(id__in=care_team_membership)
    
    try:
                
        context['cases_datagrid'] = CaseDataGrid(request, qset=cases,qtitle=qtitle)
    except Exception, e:
        print "error with the stoopid case data grid %s" % str(e)
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def view_careteam(request, careteam_id, template_name="ashandapp/view_careteam.html"):    
    context = {}
    careteam = CareTeam.objects.get(id=careteam_id)
    context['careteam'] = careteam
                
    cases = careteam.cases.all()
    context['cases'] = cases
    cases_datagrid = CaseDataGrid(request, qset=cases,qtitle="Cases for careteam")
    context['cases_datagrid'] = cases_datagrid
    context['patient']= Patient.objects.get(user=careteam.patient)
    
    provider_links_raw = careteam.providerlink_set.all()
    provider_dict = {}
    
    for plink in provider_links_raw:
        puser = plink.provider
        prov = Provider.objects.filter(user=puser)
        provider_dict[prov[0]] = plink
    context['provider_dict'] = provider_dict
    
    return render_to_response(template_name, context, context_instance=RequestContext(request))


@login_required
def dashboard(request, template_name="ashandapp/dashboard.html"):
    context = {}
    user = request.user
    profile = CaseProfile.objects.get(user = user)
    filter_datagrid = CaseDataGrid(request, qset=profile.last_filter.get_filter_queryset(), qtitle=profile.last_filter.description)
    
    context['filter_datagrid'] = filter_datagrid
    context['profile'] = profile    
    context['filter'] = profile.last_filter
    return render_to_response(template_name, context, context_instance=RequestContext(request))