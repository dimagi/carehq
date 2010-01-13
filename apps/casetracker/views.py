import logging
import hashlib
import settings
import traceback
import sys
import os
import uuid
import string
from datetime import timedelta

from django.http import HttpResponse,Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from django.db.models.query_utils import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import User 
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page

from casetracker.models import Case, CaseEvent, Filter, GridPreference, EventActivity

from datagrids import CaseDataGrid, CaseEventDataGrid, FilterDataGrid

#use in sorting
from casetracker.queries.caseevents import sort_by_person, sort_by_case, sort_by_activity, sort_by_category, get_latest_for_cases
from ashandapp.views.users import get_sorted_dictionary
from casetracker.forms import CaseModelForm, CaseCommentForm

#taken from the threadecomments django project
def _get_next(request):
    """
    The part that's the least straightforward about views in this module is how they 
    determine their redirects after they have finished computation.

    In short, they will try and determine the next place to go in the following order:

    1. If there is a variable named ``next`` in the *POST* parameters, the view will
    redirect to that variable's value.
    2. If there is a variable named ``next`` in the *GET* parameters, the view will
    redirect to that variable's value.
    3. If Django can determine the previous page from the HTTP headers, the view will
    redirect to that previous page.
    4. Otherwise, the view raise a 404 Not Found.
    """
    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', None)))
    if not next or next == request.path:
        raise Http404 # No next url was supplied in GET or POST.
    return next

def edit_case(request, case_id, template_name='casetracker/manage/edit_case.html'):
    context = {}    
    edit_mode = None
    for key, value in request.GET.items():
        if key == "action":
            edit_mode = value    
    context['case'] = Case.objects.get(id=case_id)    
    if request.method == 'POST':
        form = CaseModelForm(data=request.POST, instance=context['case'], editor_user=request.user, mode=edit_mode)
        if form.is_valid():    
            case = form.save(commit=False)
            if form.cleaned_data.has_key('comment') and form.cleaned_data['comment'] != '':
                case.edit_comment = form.cleaned_data["comment"]
            case.last_edit_by = request.user
            case.save()
            return HttpResponseRedirect(reverse('view-case', kwargs= {'case_id': case_id}))
        
    else:
        context['form'] = CaseModelForm(instance=context['case'], editor_user = request.user, mode=edit_mode)
        return render_to_response(template_name, context,context_instance=RequestContext(request))


def grid_examples(request, template_name='casetracker/examples.html'):
    context = {}    
    filtergrid = FilterDataGrid(request)
    recent_cases_grid = CaseDataGrid(request, qset=Case.objects.order_by('-opened_date'),qtitle="Recently Opened Cases")
    recent_cases_grid.paginate_by = 10
    context['filtergrid'] = filtergrid
    context['casegrid'] = recent_cases_grid
    return render_to_response(template_name, context,context_instance=RequestContext(request))

@cache_page(60 * 5)
def all_cases(request, template_name="casetracker/case_datagrid.html"):
    context = {}
    #paginate_by
    return CaseDataGrid(request).render_to_response(template_name)    
#@cache_page(60 * 1)


def case_comment(request, case_id, template_name='casetracker/view_case.html'):
    context = {}
    case = Case.objects.get(id=case_id)
    
    if request.method == 'POST':
        form = CaseCommentForm(data=request.POST)
        if form.is_valid():    
            if form.cleaned_data.has_key('comment') and form.cleaned_data['comment'] != '':
                comment = form.cleaned_data["comment"]
            evt = CaseEvent()
            evt.case = case
            evt.notes = comment
            evt.activity = EventActivity.objects.filter(category=case.category)[0]
            evt.created_by = request.user            
            evt.save()
            return HttpResponseRedirect(reverse('view-case', kwargs= {'case_id': case_id}))
    
    return HttpResponseRedirect(_get_next(request))

def view_case(request, case_id, template_name='casetracker/view_case.html'):
    context = {}
    #events = CaseEventDataGrid(request, case_id)
    #context['case_events'] = events
    
    sorting = None
    try:
        for key, value in request.GET.items():
            if key == "sort":
                sorting = value
    except:
        sorting = None
    
    thecase = Case.objects.select_related('opened_by','last_edit_by','resolved_by','closed_by','assigned_to').get(id=case_id)
    context['events'] = CaseEvent.objects.filter(case__id=case_id)
    context['case'] = thecase
    context['formatting'] = False
    context['custom_activity'] = EventActivity.objects.filter(category=thecase.category).filter(event_class='custom')
    
    
    ret = context['events'] 
    
#    if sorting == "person":
#        ret.sort(sort_by_person)
#    elif sorting == "activity":
#        ret.sort(sort_by_activity)
##    elif sorting == "category":
#        ret.sort(sort_by_category)
#    elif sorting == "case":
#        ret.sort(sort_by_case)
    
#    sorted_dic = {}
    sorted_dic = get_sorted_dictionary(sorting, ret)
    
    if len(sorted_dic) > 0:
        context['events'] = sorted_dic
        context['formatting'] = True
        
    return render_to_response(template_name, context,context_instance=RequestContext(request))

def all_case_events(request, template_name='casetracker/case_event_datagrid.html'):
    return CaseEventDataGrid(request).render_to_response(template_name)
 
def view_case_events(request, case_id, template_name='casetracker/case_event_datagrid.html'):
    return CaseEventDataGrid(request, case_id).render_to_response(template_name)
    

def all_filters(request, template_name="casetracker/filter_datagrid.html"):
    context = {}
    return FilterDataGrid(request).render_to_response(template_name)    

def newsfeed_allcases(request, template_name="casetracker/newsfeed_allcases.html"):
    context = {}
    context['cases'] = Case.objects.all()[0:10]
    return render_to_response(template_name, context,context_instance=RequestContext(request))




def view_filter(request, filter_id):
    context = {}
    showfilter = False
    for item in request.GET.items():
        if item[0] == 'filterinfo':
            showfilter = True
    
    if showfilter:
        template_name = "casetracker/show_filter.html"
        return render_to_response(context, template_name)
    else:
        #get the filter from the db
        filter = Filter.objects.get(id=filter_id)
        gridpref = GridPreference.objects.get(filter=filter)
        template_name='casetracker/case_datagrid.html'   
        context['cases'] = filter.get_filter_queryset()
        return CaseDataGrid(request, gridpref=gridpref).render_to_response(template_name)