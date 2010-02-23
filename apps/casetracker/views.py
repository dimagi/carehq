import logging
import hashlib
import settings
import traceback
import sys
import os
import uuid
import string
from datetime import datetime, timedelta

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

from casetracker.models import Case, CaseEvent, Filter, GridPreference, EventActivity,Status
from casetracker import constants

#use in sorting
from casetracker.queries.caseevents import sort_by_person, sort_by_case, sort_by_activity, sort_by_category, get_latest_for_cases
from casetracker.forms import CaseModelForm, CaseCommentForm, CaseResolveCloseForm

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

def get_sorted_caseevent_dictionary(sort, arr):
    sorted_dic = {} #sorted dictionary of organized events for newsfeed
    obj = None 
        
    if (sort == "person"): 
        for event in arr:
            if (obj == None):
                obj = event
                if not sorted_dic.has_key(obj.created_by.get_full_name()):
                    sorted_dic[obj.created_by.get_full_name()] = []
                sorted_dic[obj.created_by.get_full_name()].append(obj)
            elif obj.created_by.get_full_name() == event.created_by.get_full_name():
                sorted_dic[obj.created_by.get_full_name()].append(event)
            else :
                obj = event
                if not sorted_dic.has_key(obj.created_by.get_full_name()): 
                    sorted_dic[obj.created_by.get_full_name()] = []
                sorted_dic[obj.created_by.get_full_name()].append(obj)
    elif (sort == "category"): 
        for event in arr:
            if (obj == None):
                obj = event
                if not sorted_dic.has_key(obj.activity.category.category):
                    sorted_dic[obj.activity.category.category] = []
                sorted_dic[obj.activity.category.category].append(obj)
            elif obj.activity.category.category == event.activity.category.category:
                sorted_dic[obj.activity.category.category].append(event)
            else :
                obj = event
                if not sorted_dic.has_key(obj.activity.category.category):
                    sorted_dic[obj.activity.category.category] = []
                sorted_dic[obj.activity.category.category].append(obj)
    elif (sort == "activity"):            
        for event in arr:
            if (obj == None):
                obj = event
                if not sorted_dic.has_key(obj.activity.name):
                    sorted_dic[obj.activity.name] = []
                sorted_dic[obj.activity.name].append(obj)
            elif obj.activity.name == event.activity.name:
                sorted_dic[obj.activity.name].append(event)                
            else :
                obj = event
                if not sorted_dic.has_key(obj.activity.name):
                    sorted_dic[obj.activity.name] = [] 
                sorted_dic[obj.activity.name].append(obj)                
    elif (sort == "case"):            
        for event in arr:
            if (obj == None):
                obj = event
                if not sorted_dic.has_key(obj.case.case_name_url()):
                    sorted_dic[obj.case.case_name_url()] = []
                sorted_dic[obj.case.case_name_url()].append(obj)
            elif obj.case.id == event.case.id:
                sorted_dic[obj.case.case_name_url()].append(event)                
            else :
                obj = event
                if not sorted_dic.has_key(obj.case.case_name_url()):
                    sorted_dic[obj.case.case_name_url()] = [] 
                sorted_dic[obj.case.case_name_url()].append(obj) 
    
    return sorted_dic




def close_or_resolve_case(request, case_id, edit_mode=None, template_name = 'casetracker/manage/edit_case.html'):
    context = {}    
    case = Case.objects.get(id=case_id)
    
    if edit_mode == constants.CASE_STATE_CLOSED:
        context['edit_headline'] = "Close " + case.category.category
        event_class = constants.CASE_EVENT_CLOSE
        
    elif edit_mode == constants.CASE_STATE_RESOLVED:
        context['edit_headline'] = "Resolve " + case.category.category
        event_class = constants.CASE_EVENT_RESOLVE
    
    context['case'] = case
    if request.method == 'POST':
        form = CaseResolveCloseForm(data=request.POST, case=case, mode=edit_mode)
        if form.is_valid():
             
            status = form.cleaned_data['state']
            #activity = form.cleaned_data['event_activity']
            comment = form.cleaned_data['comment']
            
            #just grab the first close/resolve event class
            activity = EventActivity.objects.filter(category=case.category).filter(event_class=event_class)[0]
            case.status = status 
            case.last_edit_by = request.user
            case.edit_comment = comment
            case.event_activity = activity
            
            if edit_mode == constants.CASE_STATE_CLOSED:
                case.closed_by=request.user
            elif edit_mode == constants.CASE_STATE_RESOLVED:
                case.resolved_by=request.user

            case.save()
            
            return HttpResponseRedirect(reverse('view-case', kwargs= {'case_id': case_id}))
    else:
        context['form'] = CaseResolveCloseForm(case=case, mode=edit_mode)
        return render_to_response(template_name, context,context_instance=RequestContext(request))



def get_case_form(case, edit_mode):
    pass
         

def edit_case(request, case_id, template_name='casetracker/manage/edit_case.html'):
    context = {}    
    edit_mode = None
    for key, value in request.GET.items():
        if key == "action":
            edit_mode = value    

    oldcase = Case.objects.get(id=case_id)
    
    if edit_mode == "assign":
        context['edit_headline'] = "Assign " + oldcase.category.category    
    elif edit_mode == "edit":
        context['edit_headline'] = "Edit " + oldcase.category.category            
    
    context['case'] = oldcase     
    if request.method == 'POST':
        form = CaseModelForm(data=request.POST, instance=context['case'], editor_user=request.user, mode=edit_mode)
        if form.is_valid():    
            case = form.save(commit=False)
            case.edit_comment = '' #set the property to modify
                        
            if form.cleaned_data.has_key('comment') and form.cleaned_data['comment'] != '':
                case.edit_comment = form.cleaned_data["comment"]
            case.last_edit_by = request.user            
            #next, we need to see the mode and flip the fields depending on who does what.
            if edit_mode == CaseModelForm.EDIT_ASSIGN:
                
                
                case.assigned_date = datetime.utcnow()                
                case.edit_comment += " (Assigned to %s by %s)" % (case.assigned_to.first_name + " " + case.assigned_to.last_name, request.user.first_name + " " + request.user.last_name)           
            
            case.save()
            return HttpResponseRedirect(reverse('view-case', kwargs= {'case_id': case_id}))
        else:
            context['form'] = form
        
    else:
        context['form'] = CaseModelForm(instance=context['case'], editor_user = request.user, mode=edit_mode)
    
    
    return render_to_response(template_name, context,context_instance=RequestContext(request))


        
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
            evt.activity = EventActivity.objects.filter(category=case.category)\
                .filter(event_class=constants.CASE_EVENT_COMMENT)[0]
            evt.created_by = request.user            
            evt.save()
            return HttpResponseRedirect(reverse('view-case', kwargs= {'case_id': case_id}))
    
    return HttpResponseRedirect(_get_next(request))


@login_required
def view_case(request, case_id): #template_name='casetracker/view_case.html'
    context = {}
    
    thecase = Case.objects.select_related('opened_by','last_edit_by',\
                                          'resolved_by','closed_by','assigned_to',
                                          'priority','category','status').get(id=case_id)
    
#    sorting = None
    do_edit=False    
    edit_mode = None
    for key, value in request.GET.items():            
#        if key == "sort":
#            sorting = value
        if key == 'action':            
            edit_mode = value

    #context['events'] = CaseEvent.objects.select_related('created_by','activity').filter(case=thecase)
    context['case'] = thecase        
    context['custom_activity'] = EventActivity.objects.filter(category=thecase.category).filter(event_class='event-custom')
    
    template_name = thecase.category.handler.get_view_template()    
    context = thecase.category.handler.process_context(thecase,request,context)
        
#    context['formatting'] = False
#    ret = context['events']
#    event_dic = get_sorted_caseevent_dictionary(sorting, ret)
#    if len(event_dic) > 0:
#        context['events'] = event_dic
#        context['formatting'] = True


    #ok, because we're doing inline forms now, we need to be a little fancier about how we represent all this.

    if edit_mode:
        if edit_mode =='edit':
            context['form_headline'] = "Edit " + thecase.category.category
        elif edit_mode == constants.CASE_STATE_CLOSED:
            context['form_headline'] = "Close " + thecase.category.category            
        elif edit_mode == constants.CASE_STATE_RESOLVED:
            context['form_headline'] = "Resolve " + thecase.category.category            
        elif edit_mode == 'assign':            
            context['form_headline'] = "Assign " + thecase.category.category
        elif edit_mode == 'comment':            
            #context['form_headline'] = "Assign " + thecase.category.category
            pass            
            
            
        if edit_mode == 'edit' or edit_mode== 'assign':
            context['form'] = CaseModelForm(instance=thecase, editor_user = request.user, mode=edit_mode)
            context['submit_url'] = ''
            context['show_form'] = True
        elif edit_mode == constants.CASE_STATE_RESOLVED or edit_mode == constants.CASE_STATE_CLOSED:
            context['form'] = CaseResolveCloseForm(case=thecase, mode=edit_mode)
            context['submit_url'] = ''
            context['show_form'] = True
        elif edit_mode == 'comment':
            context['show_form'] = False
            context['show_comment'] = True
            
        if request.method == 'POST': 
            if edit_mode == 'edit' or edit_mode== 'assign':
                form = CaseModelForm(data=request.POST, instance=thecase, editor_user=request.user, mode=edit_mode)
                context['form'] = form
                if form.is_valid():    
                    case = form.save(commit=False)
                    case.edit_comment = '' #set the property to modify
                                
                    if form.cleaned_data.has_key('comment') and form.cleaned_data['comment'] != '':
                        case.edit_comment = form.cleaned_data["comment"]
                    case.last_edit_by = request.user
                    
                    #next, we need to see the mode and flip the fields depending on who does what.
                    if edit_mode == CaseModelForm.EDIT_ASSIGN:
                        case.assigned_date = datetime.utcnow()
                        case.edit_comment += " (Assigned to %s by %s)" % (case.assigned_to.first_name + " " + case.assigned_to.last_name, request.user.first_name + " " + request.user.last_name)
                        #now that we've assigned it, we can flip the state
                        if case.status.state_class == constants.CASE_STATE_NEW:                
                            case.status = Status.objects.filter(category=case.category).filter(state_class=constants.CASE_STATE_OPEN)[0]                    
                    case.save()
                    return HttpResponseRedirect(reverse('view-case', kwargs= {'case_id': case_id}))                    
            elif edit_mode == constants.CASE_STATE_RESOLVED or edit_mode == constants.CASE_STATE_CLOSED:
                form = CaseResolveCloseForm(data=request.POST, case=thecase, mode=edit_mode)
                
                if edit_mode == constants.CASE_STATE_CLOSED:
                    event_class = constants.CASE_EVENT_CLOSE
        
                elif edit_mode == constants.CASE_STATE_RESOLVED:
                    event_class = constants.CASE_EVENT_RESOLVE

                context['form'] = form
                if form.is_valid():
                     
                    status = form.cleaned_data['state']
                    #activity = form.cleaned_data['event_activity']
                    comment = form.cleaned_data['comment']
                    
                    #just grab the first close/resolve event class
                    activity = EventActivity.objects.filter(category=thecase.category).filter(event_class=event_class)[0]
                    thecase.status = status 
                    thecase.last_edit_by = request.user
                    thecase.edit_comment = comment
                    thecase.event_activity = activity
                    
                    if edit_mode == constants.CASE_STATE_CLOSED:
                        thecase.closed_by=request.user
                    elif edit_mode == constants.CASE_STATE_RESOLVED:
                        thecase.resolved_by=request.user
        
                    thecase.save()
                    
                    return HttpResponseRedirect(reverse('view-case', kwargs= {'case_id': case_id}))                    
            elif edit_mode == 'comment':
                form = CaseCommentForm(data=request.POST)
                context['form'] = form
                if form.is_valid():    
                    if form.cleaned_data.has_key('comment') and form.cleaned_data['comment'] != '':
                        comment = form.cleaned_data["comment"]
                    evt = CaseEvent()
                    evt.case = thecase
                    evt.notes = comment
                    evt.activity = EventActivity.objects.filter(category=thecase.category)\
                        .filter(event_class=constants.CASE_EVENT_COMMENT)[0]
                    evt.created_by = request.user            
                    evt.save()
                    return HttpResponseRedirect(reverse('view-case', kwargs= {'case_id': case_id}))
        
         
    return render_to_response(template_name, context, context_instance=RequestContext(request))


@login_required
#@cache_page(60 * 1)
def case_newsfeed(request, case_id, template_name='casetracker/partials/newsfeed_inline.html'):
    context = {}
    thecase = Case.objects.select_related('opened_by','last_edit_by',\
                                          'resolved_by','closed_by','assigned_to',
                                          'priority','category','status').get(id=case_id)
    
    sorting = None
    do_edit=False    
    edit_mode = None
    for key, value in request.GET.items():            
        if key == "sort":
            sorting = value
    
    context['events'] = CaseEvent.objects.select_related('created_by','activity').filter(case=thecase)
    context['case'] = thecase        
    context['custom_activity'] = EventActivity.objects.filter(category=thecase.category).filter(event_class='event-custom')
    
    context['formatting'] = False
    event_arr = context['events']
    event_dic = get_sorted_caseevent_dictionary(sorting, event_arr)
    if len(event_dic) > 0:
        context['events'] = event_dic
        context['formatting'] = True
    return render_to_response(template_name, context, context_instance=RequestContext(request))

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
        return render_to_response(context, template_name)        