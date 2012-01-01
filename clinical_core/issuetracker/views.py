import logging
from datetime import datetime
from django.contrib.auth.models import User
from django.http import  Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from issuetracker.models import Issue, IssueEvent
from issuetracker import constants
from issuetracker.feeds.issueevents import get_sorted_issueevent_dictionary
from issuetracker.forms import CaseModelForm, CaseCommentForm, CaseResolveCloseForm

#taken from the threadecomments django project
from issuetracker.models.filters import Filter
from patient.models import Patient
from permissions.models import Actor

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


from issuetracker.managers.issuemanager import IssueManager
issuemanager = IssueManager()
@login_required
def all_issues(request, template_name='issuetracker/issues_list.html'):
    context = RequestContext(request)
    start = request.GET.get('start', 0)
    count = request.GET.get('count',50)
    group_by = request.GET.get('groupBy','opened_date')

    issues = Issue.objects.all().select_related('opened_by','assigned_to','last_edit_by')
    context['issues'] = issues
    context['columns'] = ['opened_date', 'opened_by', 'assigned_to','description', 'last_edit_date', 'last_edit_by']

    return render_to_response(template_name, context_instance=context)





@login_required
def manage_issue(request, issue_id, template_name='issuetracker/manage_issue.html'):
    """
    This view handles all aspects of lifecycle depending on the URL params and the request type.
    """
    context = RequestContext(request)
    theissue = Issue.objects.get(id=issue_id)

    do_edit = False    
    activity_slug = None
    activity = None
    for key, value in request.GET.items():            
        if key == 'activity':            
            activity = value
    context['issue'] = theissue
   
    ########################
    # Inline Form display
    if activity:                
        context['show_form'] = True
        context['form_headline' ] = activity

        if request.method == 'POST':
            if activity == constants.CASE_EVENT_EDIT or activity == constants.CASE_EVENT_ASSIGN:
                form = CaseModelForm(data=request.POST, instance=theissue, editor_user=request.user, activity=activity)
                context['form'] = form
                if form.is_valid():                    
                    issue = form.save(commit=False)
                    edit_comment = form.cleaned_data["comment"]
                    issue.last_edit_by = request.user
                    issue.last_edit_date = datetime.utcnow()
                    #next, we need to see the mode and flip the fields depending on who does what.
                    if activity == constants.CASE_EVENT_ASSIGN:
                        issue.assigned_date = datetime.utcnow()
                        issue.assigned_by = request.user
                        edit_comment += " (%s to %s by %s)" % (activity.past_tense.title(), issue.assigned_to.title(), request.user.title())
                        
                    issue.save(activity=activity, save_comment = edit_comment)
                    return HttpResponseRedirect(reverse('manage-issue', kwargs= {'issue_id': issue_id}))
            
            elif activity == constants.CASE_EVENT_RESOLVE or activity == constants.CASE_EVENT_CLOSE:
                form = CaseResolveCloseForm(data=request.POST, issue=theissue, activity=activity)
                context['form'] = form
                if form.is_valid():                     
                    status = form.cleaned_data['state']                    
                    comment = form.cleaned_data['comment']                    
                    theissue.status = status
                    theissue.last_edit_by = request.user
                    
                    if activity == constants.CASE_EVENT_CLOSE:
                        theissue.closed_by=request.user
                    elif activity == constants.CASE_EVENT_RESOLVE:
                        theissue.resolved_by=request.user
        
                    theissue.save(activity = activity, save_comment = comment)
                    
                    return HttpResponseRedirect(reverse('manage-issue', kwargs= {'issue_id': issue_id}))
            elif activity == constants.CASE_EVENT_COMMENT:
                form = CaseCommentForm(data=request.POST)
                context['form'] = form
                if form.is_valid():    
                    if form.cleaned_data.has_key('comment') and form.cleaned_data['comment'] != '':
                        comment = form.cleaned_data["comment"]
                    evt = IssueEvent()
                    evt.issue = theissue
                    evt.notes = comment
                    evt.activity = constants.CASE_EVENT_COMMENT
                    evt.created_by = request.user
                    evt.save()
                    return HttpResponseRedirect(reverse('manage-issue', kwargs= {'issue_id': issue_id}))
        else:
            #it's a GET
            if activity==constants.CASE_EVENT_EDIT or activity==constants.CASE_EVENT_ASSIGN:
                issueform = CaseModelForm
            elif activity == constants.CASE_EVENT_COMMENT:
                issueform = CaseCommentForm
            elif activity==constants.CASE_EVENT_RESOLVE or activity==constants.CASE_EVENT_CLOSE:
                issueform = CaseResolveCloseForm

            # This is a bit ugly at the moment as this view itself is the only place that instantiates the forms 
            if issueform == CaseModelForm:
                context['form'] = issueform(instance=theissue, editor_user=request.user, activity=activity)
                context['can_comment'] = False
            elif issueform== CaseResolveCloseForm:
                context['form'] = issueform(issue=theissue, activity=activity)
                context['can_comment'] = False                        
            elif issueform == CaseCommentForm:
                context['form'] = issueform()
                        
                
            else:
                logging.error("no form definition")
            context['submit_url'] = ''    
    return render_to_response(template_name, context_instance=context)


@login_required
#@cache_page(60 * 1)
def issue_newsfeed(request, issue_id, template_name='issuetracker/partials/newsfeed_inline.html'):
    """
    Generic inline view for all CaseEvents related to a Issue.
    
    This is called form tabbed_newsfeed.html via the jQuery UI Tab control.
    """
    context = {}
#    theissue = Issue.objects.select_related('opened_by','last_edit_by',\
#                                          'resolved_by','closed_by','assigned_to',
#                                          'priority','category','status').get(id=issue_id)
#
#    sorting = None
#    do_edit=False
#    edit_mode = None
#    for key, value in request.GET.items():
#        if key == "sort":
#            sorting = value
#
#    context['events'] = IssueEvent.objects.select_related('created_by','activity').filter(issue=theissue).order_by('created_date')
#    context['issue'] = theissue
#    context['custom_activity'] = ActivityClass.objects.filter(event_class='event-custom')
#    context['formatting'] = False
#    event_arr = context['events']
#    event_dic = get_sorted_issueevent_dictionary(sorting, event_arr)
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
    context['filter_issues'] = qset

    template_name='issuetracker/filter/filter_simpletable.html'
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def debug_reference(request, template_name="issuetracker/debug_reference.html"):
    users = User.objects.all()
    roles = Actor.objects.all()
    patients = Patient.objects.all()
    context = RequestContext(request)
    context['users'] = users
    context['roles'] = roles
    context['patients'] = patients
    return render_to_response(template_name, context_instance=context)


def all_users(request, template_name="issuetracker/all_users.html"):
    users = User.objects.all()
    context = RequestContext(request)
    context['users'] = users
    return render_to_response(template_name, context_instance=context)

def all_roles(request, template_name="issuetracker/all_roles.html"):
    roles = Roles.objects.all()
    context = RequestContext(request)
    context['roles'] = roles
    return render_to_response(template_name, context_instance=context)

def all_patients(request, template_name="issuetracker/all_patients.html"):
    patients = Patient.objects.all()
    context = RequestContext(request)
    context['patients'] = patients
    return render_to_response(template_name, context_instance=context)

def user_issues(request, user_id, template_name="issuetracker/user_issues.html"):
    issuefilter = str(request.GET.get('issuefilter', 'opened_by'))

    context = RequestContext(request)
    user = User.objects.get(id=user_id)
    roles = Actor.identities.for_user(user)
    role_issues = [(role, Issue.objects.filter(**{issuefilter: role}))for role in roles]

    context['user'] = user
    context['issuefilter'] = issuefilter
    context['role_issues'] = role_issues
    context['columns'] = ['opened_date', 'opened_by', 'assigned_to','description', 'last_edit_date', 'last_edit_by']
    return render_to_response(template_name, context_instance=context)

def role_issues(request, role_id, template_name="issuetracker/role_issues.html"):
    context = RequestContext(request)
    role = Actor.objects.get(id=role_id)
    issuefilter = str(request.GET.get('issuefilter', 'opened_by'))
    issues = Issue.objects.filter(**{issuefilter:role})

    context['role'] = role
    context['issues'] = issues
    context['issuefilter'] = issuefilter
    context['columns'] = ['opened_date', 'opened_by', 'assigned_to','description', 'last_edit_date', 'last_edit_by']
    return render_to_response(template_name, context_instance=context)

def patient_issues(request, patient_id, template_name="issuetracker/patient_issues.html"):
    context = RequestContext(request)
    patient = Patient.objects.get(id=patient_id)
    issues = Issue.objects.filter(patient=patient)
    context['columns'] = ['opened_date', 'opened_by', 'assigned_to','description', 'last_edit_date', 'last_edit_by']
    context['patient'] = patient
    context['issues'] = issues
    return render_to_response(template_name, context_instance=context)

