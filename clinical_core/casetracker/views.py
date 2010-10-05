import logging
from datetime import datetime
from django.http import  Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from auditor.decorators import log_access
from casetracker.models import Case, CaseEvent, Filter, ActivityClass
from casetracker import constants
from casetracker.feeds.caseevents import get_sorted_caseevent_dictionary
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


#
#def close_or_resolve_case(request, case_id, edit_mode=None, template_name = 'casetracker/manage/edit_case.html'):
#    context = {}    
#    case = Case.objects.get(id=case_id)
#    
#    if edit_mode == constants.CASE_STATE_CLOSED:
#        context['edit_headline'] = "Close " + case.category.slug
#        event_class = constants.CASE_EVENT_CLOSE
#        
#    elif edit_mode == constants.CASE_STATE_RESOLVED:
#        context['edit_headline'] = "Resolve " + case.category.slug
#        event_class = constants.CASE_EVENT_RESOLVE
#    
#    context['case'] = case
#    if request.method == 'POST':
#        form = CaseResolveCloseForm(data=request.POST, case=case, activity_slug=edit_mode)
#        if form.is_valid():
#             
#            status = form.cleaned_data['state']
#            #activity = form.cleaned_data['event_activity']
#            comment = form.cleaned_data['comment']
#            
#            #just grab the first close/resolve event class
#            activity = ActivityClass.objects.filter(category=case.category).filter(event_class=event_class)[0]
#            case.status = status 
#            case.last_edit_by = request.user
#            case.edit_comment = comment
#            case.event_activity = activity
#            
#            if edit_mode == constants.CASE_STATE_CLOSED:
#                case.closed_by=request.user
#            elif edit_mode == constants.CASE_STATE_RESOLVED:
#                case.resolved_by=request.user
#
#            case.save()
#            
#            return HttpResponseRedirect(reverse('manage-case', kwargs= {'case_id': case_id}))
#    else:
#        context['form'] = CaseResolveCloseForm(case=case, activity_slug=edit_mode)
#        return render_to_response(template_name, context,context_instance=RequestContext(request))
#
#
#
#def get_case_form(case, edit_mode):
#    pass
#         
#
#def edit_case(request, case_id, template_name='casetracker/manage/edit_case.html'):
#    context = {}    
#    edit_mode = None
#    for key, value in request.GET.items():
#        if key == "action":
#            edit_mode = value    
#
#    oldcase = Case.objects.get(id=case_id)
#    
#    if edit_mode == "assign":
#        context['edit_headline'] = "Assign " + oldcase.category.slug    
#    elif edit_mode == "edit":
#        context['edit_headline'] = "Edit " + oldcase.category.slug            
#    
#    context['case'] = oldcase     
#    if request.method == 'POST':
#        form = CaseModelForm(data=request.POST, instance=context['case'], editor_user=request.user, mode=edit_mode)
#        if form.is_valid():    
#            case = form.save(commit=False)
#            case.edit_comment = '' #set the property to modify
#                        
#            if form.cleaned_data.has_key('comment') and form.cleaned_data['comment'] != '':
#                case.edit_comment = form.cleaned_data["comment"]
#            case.last_edit_by = request.user            
#            #next, we need to see the mode and flip the fields depending on who does what.
#            if edit_mode == CaseModelForm.EDIT_ASSIGN:
#                
#                
#                case.assigned_date = datetime.utcnow()                
#                case.edit_comment += " (Assigned to %s by %s)" % (case.assigned_to.first_name + " " + case.assigned_to.last_name, request.user.first_name + " " + request.user.last_name)           
#            
#            case.save()
#            return HttpResponseRedirect(reverse('manage-case', kwargs= {'case_id': case_id}))
#        else:
#            context['form'] = form
#        
#    else:
#        context['form'] = CaseModelForm(instance=context['case'], editor_user = request.user, mode=edit_mode)
#    
#    
#    return render_to_response(template_name, context,context_instance=RequestContext(request))

#
#        
##@cache_page(60 * 1)
#def case_comment(request, case_id, template_name='casetracker/manage_case.html'):
#    context = {}
#    case = Case.objects.get(id=case_id)
#    
#    if request.method == 'POST':
#        form = CaseCommentForm(data=request.POST)
#        if form.is_valid():    
#            if form.cleaned_data.has_key('comment') and form.cleaned_data['comment'] != '':
#                comment = form.cleaned_data["comment"]
#            evt = CaseEvent()
#            evt.case = case
#            evt.notes = comment
#            evt.activity = ActivityClass.objects.filter(category=case.category)\
#                .filter(event_class=constants.CASE_EVENT_COMMENT)[0]
#            evt.created_by = request.user            
#            evt.save()
#            return HttpResponseRedirect(reverse('manage-case', kwargs= {'case_id': case_id}))
#    
#    return HttpResponseRedirect(_get_next(request))


@login_required
@log_access
def manage_case(request, case_id): #template_name='casetracker/manage_case.html'
    """
    This view handles all aspects of lifecycle depending on the URL params and the request type.
    """
    context = RequestContext(request)
    
    thecase = Case.objects.select_related('opened_by','last_edit_by',\
                                          'resolved_by','closed_by','assigned_to',
                                          'priority','category','status').get(id=case_id)
    

    do_edit = False    
    activity_slug = None
    activity = None
    for key, value in request.GET.items():            
        if key == 'activity':            
            activity = ActivityClass.objects.get(slug=value)
    context['case'] = thecase
   
    template_name = thecase.category.handler.read_template(request, context)
    context = thecase.category.handler.read_context(thecase,request, context)

    ########################
    # Inline Form display
    if activity:                
        context['show_form'] = True
        context['form_headline' ] = activity.active_tense.title()            
        
        if request.method == 'POST': 
            if activity.event_class == constants.CASE_EVENT_EDIT or activity.event_class == constants.CASE_EVENT_ASSIGN:
                form = CaseModelForm(data=request.POST, instance=thecase, editor_user=request.user, activity=activity)
                context['form'] = form
                if form.is_valid():                    
                    case = form.save(commit=False)
                    edit_comment = form.cleaned_data["comment"]
                    case.last_edit_by = request.user
                    case.last_edit_date = datetime.utcnow()                    
                    #next, we need to see the mode and flip the fields depending on who does what.
                    if activity.event_class == constants.CASE_EVENT_ASSIGN:
                        case.assigned_date = datetime.utcnow()
                        case.assigned_by = request.user            
                        edit_comment += " (%s to %s by %s)" % (activity.past_tense.title(), case.assigned_to.get_full_name(), request.user.get_full_name())
                        
                    case.save(activity=activity, save_comment = edit_comment)                                        
                    return HttpResponseRedirect(reverse('manage-case', kwargs= {'case_id': case_id}))            
            
            elif activity.event_class == constants.CASE_EVENT_RESOLVE or activity.event_class == constants.CASE_EVENT_CLOSE:
                form = CaseResolveCloseForm(data=request.POST, case=thecase, activity=activity)
                context['form'] = form
                if form.is_valid():                     
                    status = form.cleaned_data['state']                    
                    comment = form.cleaned_data['comment']                    
                    thecase.status = status 
                    thecase.last_edit_by = request.user
                    
                    if activity.event_class == constants.CASE_EVENT_CLOSE:
                        thecase.closed_by=request.user
                    elif activity.event_class == constants.CASE_EVENT_RESOLVE:
                        thecase.resolved_by=request.user
        
                    thecase.save(activity = activity, save_comment = comment)
                    
                    return HttpResponseRedirect(reverse('manage-case', kwargs= {'case_id': case_id}))                    
            elif activity.event_class == constants.CASE_EVENT_COMMENT:
                form = CaseCommentForm(data=request.POST)
                context['form'] = form
                if form.is_valid():    
                    if form.cleaned_data.has_key('comment') and form.cleaned_data['comment'] != '':
                        comment = form.cleaned_data["comment"]
                    evt = CaseEvent()
                    evt.case = thecase
                    evt.notes = comment
                    evt.activity = ActivityClass.objects.filter(category=thecase.category)\
                        .filter(event_class=constants.CASE_EVENT_COMMENT)[0]
                    evt.created_by = request.user            
                    evt.save()
                    return HttpResponseRedirect(reverse('manage-case', kwargs= {'case_id': case_id}))
        else:
            #it's a GET
            caseform = activity.bridge.form_class()
            # This is a bit ugly at the moment as this view itself is the only place that instantiates the forms 
            if caseform == CaseModelForm:
                context['form'] = caseform(instance=thecase, editor_user=request.user, activity=activity)
                context['can_comment'] = False
            elif caseform== CaseResolveCloseForm:
                context['form'] = caseform(case=thecase, activity=activity)
                context['can_comment'] = False                        
            elif caseform == CaseCommentForm:
                context['form'] = caseform()
                        
                
            else:
                logging.error("no form definition")
            context['submit_url'] = ''    
    return render_to_response(template_name, context_instance=context)


@login_required
#@cache_page(60 * 1)
def case_newsfeed(request, case_id, template_name='casetracker/partials/newsfeed_inline.html'):
    """
    Generic inline view for all CaseEvents related to a Case.
    
    This is called form tabbed_newsfeed.html via the jQuery UI Tab control.
    """
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
    
    context['events'] = CaseEvent.objects.select_related('created_by','activity').filter(case=thecase).order_by('created_date')
    context['case'] = thecase        
    context['custom_activity'] = ActivityClass.objects.filter(event_class='event-custom')
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
    filter = Filter.objects.get(id=filter_id)
    gridpref = filter.gridpreference
    
    group_by = None
    for key, value in request.GET.items():            
        if key == "groupBy":
            group_by_col = value
    
    split_headings = True
    qset = filter.get_filter_queryset()    
    
    
    context['filter'] = filter
    context['gridpref'] = gridpref
    
        
    context['filter_cases'] = qset
    template_name='casetracker/filter/filter_simpletable.html'
    return render_to_response(template_name, context, context_instance=RequestContext(request))







