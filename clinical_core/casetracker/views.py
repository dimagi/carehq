import logging
from datetime import datetime
from django.contrib.auth.models import User
from django.http import  Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from actors.models.roles import Role
from casetracker.models import Case, CaseEvent
from casetracker import constants
from casetracker.feeds.caseevents import get_sorted_caseevent_dictionary
from casetracker.forms import CaseModelForm, CaseCommentForm, CaseResolveCloseForm

#taken from the threadecomments django project
from casetracker.models.filters import Filter
from patient.models import Patient

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


from casetracker.managers.casemanager import CaseManager
casemanager = CaseManager()
@login_required
def all_cases(request, template_name='casetracker/cases_list.html'):
    context = RequestContext(request)
    start = request.GET.get('start', 0)
    count = request.GET.get('count',50)
    group_by = request.GET.get('groupBy','opened_date')

    cases = Case.objects.all().select_related('opened_by','assigned_to','last_edit_by')
    context['cases'] = cases
    context['columns'] = ['opened_date', 'opened_by', 'assigned_to','description', 'last_edit_date', 'last_edit_by']

    return render_to_response(template_name, context_instance=context)





@login_required
def manage_case(request, case_id, template_name='casetracker/manage_case.html'):
    """
    This view handles all aspects of lifecycle depending on the URL params and the request type.
    """
    context = RequestContext(request)
    thecase = Case.objects.get(id=case_id)

    do_edit = False    
    activity_slug = None
    activity = None
    for key, value in request.GET.items():            
        if key == 'activity':            
            activity = value
    context['case'] = thecase
   
    #template_name = thecase.category.handler.read_template(request, context)
    #context = thecase.category.handler.read_context(thecase,request, context)
    ########################
    # Inline Form display
    if activity:                
        context['show_form'] = True
        context['form_headline' ] = activity

        if request.method == 'POST':
            if activity == constants.CASE_EVENT_EDIT or activity == constants.CASE_EVENT_ASSIGN:
                form = CaseModelForm(data=request.POST, instance=thecase, editor_user=request.user, activity=activity)
                context['form'] = form
                if form.is_valid():                    
                    case = form.save(commit=False)
                    edit_comment = form.cleaned_data["comment"]
                    case.last_edit_by = request.user
                    case.last_edit_date = datetime.utcnow()                    
                    #next, we need to see the mode and flip the fields depending on who does what.
                    if activity == constants.CASE_EVENT_ASSIGN:
                        case.assigned_date = datetime.utcnow()
                        case.assigned_by = request.user            
                        edit_comment += " (%s to %s by %s)" % (activity.past_tense.title(), case.assigned_to.title(), request.user.title())
                        
                    case.save(activity=activity, save_comment = edit_comment)                                        
                    return HttpResponseRedirect(reverse('manage-case', kwargs= {'case_id': case_id}))            
            
            elif activity == constants.CASE_EVENT_RESOLVE or activity == constants.CASE_EVENT_CLOSE:
                form = CaseResolveCloseForm(data=request.POST, case=thecase, activity=activity)
                context['form'] = form
                if form.is_valid():                     
                    status = form.cleaned_data['state']                    
                    comment = form.cleaned_data['comment']                    
                    thecase.status = status 
                    thecase.last_edit_by = request.user
                    
                    if activity == constants.CASE_EVENT_CLOSE:
                        thecase.closed_by=request.user
                    elif activity == constants.CASE_EVENT_RESOLVE:
                        thecase.resolved_by=request.user
        
                    thecase.save(activity = activity, save_comment = comment)
                    
                    return HttpResponseRedirect(reverse('manage-case', kwargs= {'case_id': case_id}))                    
            elif activity == constants.CASE_EVENT_COMMENT:
                form = CaseCommentForm(data=request.POST)
                context['form'] = form
                if form.is_valid():    
                    if form.cleaned_data.has_key('comment') and form.cleaned_data['comment'] != '':
                        comment = form.cleaned_data["comment"]
                    evt = CaseEvent()
                    evt.case = thecase
                    evt.notes = comment
                    evt.activity = constants.CASE_EVENT_COMMENT
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
#    thecase = Case.objects.select_related('opened_by','last_edit_by',\
#                                          'resolved_by','closed_by','assigned_to',
#                                          'priority','category','status').get(id=case_id)
#
#    sorting = None
#    do_edit=False
#    edit_mode = None
#    for key, value in request.GET.items():
#        if key == "sort":
#            sorting = value
#
#    context['events'] = CaseEvent.objects.select_related('created_by','activity').filter(case=thecase).order_by('created_date')
#    context['case'] = thecase
#    context['custom_activity'] = ActivityClass.objects.filter(event_class='event-custom')
#    context['formatting'] = False
#    event_arr = context['events']
#    event_dic = get_sorted_caseevent_dictionary(sorting, event_arr)
#    if len(event_dic) > 0:
#        context['events'] = event_dic
#        context['formatting'] = True
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

def debug_reference(request, template_name="casetracker/debug_reference.html"):
    users = User.objects.all()
    roles = Role.objects.all()
    patients = Patient.objects.all()
    context = RequestContext(request)
    context['users'] = users
    context['roles'] = roles
    context['patients'] = patients
    return render_to_response(template_name, context_instance=context)


def all_users(request, template_name="casetracker/all_users.html"):
    users = User.objects.all()
    context = RequestContext(request)
    context['users'] = users
    return render_to_response(template_name, context_instance=context)

def all_roles(request, template_name="casetracker/all_roles.html"):
    roles = Roles.objects.all()
    context = RequestContext(request)
    context['roles'] = roles
    return render_to_response(template_name, context_instance=context)

def all_patients(request, template_name="casetracker/all_patients.html"):
    patients = Patient.objects.all()
    context = RequestContext(request)
    context['patients'] = patients
    return render_to_response(template_name, context_instance=context)

def user_cases(request, user_id, template_name="casetracker/user_cases.html"):
    casefilter = str(request.GET.get('casefilter', 'opened_by'))

    context = RequestContext(request)
    user = User.objects.get(id=user_id)
    roles = Role.identities.for_user(user)
    role_cases = [(role, Case.objects.filter(**{casefilter: role}))for role in roles]

    context['user'] = user
    context['casefilter'] = casefilter
    context['role_cases'] = role_cases
    context['columns'] = ['opened_date', 'opened_by', 'assigned_to','description', 'last_edit_date', 'last_edit_by']
    return render_to_response(template_name, context_instance=context)

def role_cases(request, role_id, template_name="casetracker/role_cases.html"):
    context = RequestContext(request)
    role = Role.objects.get(id=role_id)
    casefilter = str(request.GET.get('casefilter', 'opened_by'))
    cases = Case.objects.filter(**{casefilter:role})

    context['role'] = role
    context['cases'] = cases
    context['casefilter'] = casefilter
    context['columns'] = ['opened_date', 'opened_by', 'assigned_to','description', 'last_edit_date', 'last_edit_by']
    return render_to_response(template_name, context_instance=context)

def patient_cases(request, patient_id, template_name="casetracker/patient_cases.html"):
    context = RequestContext(request)
    patient = Patient.objects.get(id=patient_id)
    cases = Case.objects.filter(patient=patient)
    context['columns'] = ['opened_date', 'opened_by', 'assigned_to','description', 'last_edit_date', 'last_edit_by']
    context['patient'] = patient
    context['cases'] = cases
    return render_to_response(template_name, context_instance=context)

