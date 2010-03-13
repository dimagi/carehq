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
                if not sorted_dic.has_key(obj.activity.category.slug):
                    sorted_dic[obj.activity.category.slug] = []
                sorted_dic[obj.activity.category.slug].append(obj)
            elif obj.activity.category.slug == event.activity.category.slug:
                sorted_dic[obj.activity.category.slug].append(event)
            else :
                obj = event
                if not sorted_dic.has_key(obj.activity.category.slug):
                    sorted_dic[obj.activity.category.slug] = []
                sorted_dic[obj.activity.category.slug].append(obj)
    elif (sort == "activity"):            
        for event in arr:
            if (obj == None):
                obj = event
                if not sorted_dic.has_key(obj.activity.slug):
                    sorted_dic[obj.activity.slug] = []
                sorted_dic[obj.activity.slug].append(obj)
            elif obj.activity.slug == event.activity.slug:
                sorted_dic[obj.activity.slug].append(event)                
            else :
                obj = event
                if not sorted_dic.has_key(obj.activity.slug):
                    sorted_dic[obj.activity.slug] = [] 
                sorted_dic[obj.activity.slug].append(obj)                
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
        context['edit_headline'] = "Close " + case.category.slug
        event_class = constants.CASE_EVENT_CLOSE
        
    elif edit_mode == constants.CASE_STATE_RESOLVED:
        context['edit_headline'] = "Resolve " + case.category.slug
        event_class = constants.CASE_EVENT_RESOLVE
    
    context['case'] = case
    if request.method == 'POST':
        form = CaseResolveCloseForm(data=request.POST, case=case, activity_slug=edit_mode)
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
        context['form'] = CaseResolveCloseForm(case=case, activity_slug=edit_mode)
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
        context['edit_headline'] = "Assign " + oldcase.category.slug    
    elif edit_mode == "edit":
        context['edit_headline'] = "Edit " + oldcase.category.slug            
    
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
    

    do_edit = False    
    activity_slug = None
    activity = None
    for key, value in request.GET.items():            
        if key == 'activity':            
            activity = EventActivity.objects.get(slug=value)
#    if activity == None:
#        activity = EventActivity.objects.get(slug=constants.CASE_EVENT_VIEW)
#        not all cases have a case_event_view activity yet defined.  not sure if this should be defined in the audit log or something else


    context['case'] = thecase
   
    template_name = thecase.category.bridge.read_template(request, context)    
    context = thecase.category.bridge.read_context(thecase,request, context)

    ########################
    # Inline Form display
    if activity:        
        activity_class = activity.event_class        
        context['form_headline'] = activity.active_tense.title()            
        caseform = activity.form_class
        # This is a bit ugly at the moment as this view itself is the only place that instantiates the forms 
        if isinstance(caseform, CaseModelForm):
            context['form'] = caseform(instance=thecase, editor_user=request.user, mode=activity_slug)                        
        elif isinstance(caseform, CaseResolveCloseForm):
            context['form'] = caseform(case=thecase, mode=activity_slug)                        
        elif isinstance(caseform, CaseCommentForm):
            context['form'] = caseform(case=thecase, mode=activity_slug)             
        context['submit_url'] = ''            

        if request.method == 'POST': 
            if activity_class == constants.CASE_EVENT_EDIT or activity_class == constants.CASE_EVENT_ASSIGN:
                form = CaseModelForm(data=request.POST, instance=thecase, editor_user=request.user, activity=activity)
                context['form'] = form
                if form.is_valid():    
                    case = form.save()                    
                    return HttpResponseRedirect(reverse('view-case', kwargs= {'case_id': case_id}))                    
            elif activity_class == constants.CASE_STATE_RESOLVED or activity_class == constants.CASE_STATE_CLOSED:
                form = CaseResolveCloseForm(data=request.POST, case=thecase, mode=activity_slug)
                
                if activity_class == constants.CASE_EVENT_CLOSE:
                    event_class = constants.CASE_EVENT_CLOSE
        
                elif activity_class == constants.CASE_STATE_RESOLVED:
                    event_class = constants.CASE_EVENT_RESOLVE

                context['form'] = form
                if form.is_valid():
                     
                    status = form.cleaned_data['state']                    
                    comment = form.cleaned_data['comment']
                    
                    activity = EventActivity.objects.filter(category=thecase.category).filter(event_class=event_class)[0]
                    thecase.status = status 
                    thecase.last_edit_by = request.user
                    thecase.edit_comment = comment
                    thecase.event_activity = activity
                    
                    if activity_slug == constants.CASE_STATE_CLOSED:
                        thecase.closed_by=request.user
                    elif activity_slug == constants.CASE_STATE_RESOLVED:
                        thecase.resolved_by=request.user
        
                    thecase.save()
                    
                    return HttpResponseRedirect(reverse('view-case', kwargs= {'case_id': case_id}))                    
            elif activity_slug == 'comment':
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