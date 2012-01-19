import logging
from datetime import datetime
import pdb
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.http import  Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from issuetracker.models import Issue, IssueEvent
from issuetracker import issue_constants
from issuetracker.feeds.issueevents import get_sorted_issueevent_dictionary
from issuetracker.forms import IssueModelForm, IssueCommentForm, IssueResolveCloseForm

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

#
#class IssueListView(TemplateView):
#    """
#    Generic class based view for viewing the patient list.
#    """
#    template_name="patient/patient_list.html"
#    patient_type=None
#    couch_view = 'patient/all'
#
#    @method_decorator(login_required)
#    def dispatch(self, *args, **kwargs):
#        return super(IssueListView,self).dispatch(*args, **kwargs)
#
#    def get_context_data(self, **kwargs):
#        context = super(PatientListView, self).get_context_data(**kwargs)
#        view_results = BasePatient.get_db().view(self.couch_view, include_docs=True).all()
#        pats = [BasePatient.get_typed_from_dict(row["doc"]) for row in view_results]
#
#        if self.patient_type != None:
#            pats = filter(lambda x: isinstance(x, self.patient_type), pats)
#        context['patients'] = pats
#        context['create_patient_url'] = reverse(self.create_patient_viewname)
#        return context
#
#
#
#class IssueSingleView(TemplateView):
#    template_name = 'patient/base_patient.html'
#    patient_list_url = '/patient/list' #hardcoded from urls, because you can't do a reverse due to the urls not being bootstrapped yet.
#    @method_decorator(login_required)
#    def dispatch(self, *args, **kwargs):
#        return super(PatientSingleView,self).dispatch(*args, **kwargs)
#    def get_context_data(self, **kwargs):
#        context = super(PatientSingleView, self).get_context_data(**kwargs)
#        params = context['params']
#        patient_guid =  params['patient_guid']
#        pat = BasePatient.get_typed_from_dict(BasePatient.get_db().get(patient_guid))
#        context['patient_doc'] = pat
#        context['patient_django'] = Patient.objects.get(doc_id=pat._id)
#        context['patient_list_url'] = self.patient_list_url
#        return context


from issuetracker.managers.issuemanager import IssueManager
issuemanager = IssueManager()
@login_required
def all_issues(request, template_name='issuetracker/issues_list.html'):
    context = RequestContext(request)
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
    activity = request.GET.get('activity',issue_constants.CASE_EVENT_COMMENT)
    context['issue'] = theissue
    context['activity'] = activity
   
    ########################
    # Inline Form display
    if activity:                
        context['show_form'] = True
        context['form_headline' ] = activity

        if request.method == 'POST':
            if activity == issue_constants.CASE_EVENT_EDIT or activity == issue_constants.CASE_EVENT_ASSIGN:
                form = IssueModelForm(data=request.POST, instance=theissue, editor_actor=request.current_actor, activity=activity)
                context['form'] = form
                if form.is_valid():                    
                    issue = form.save(commit=False)
                    edit_comment = form.cleaned_data["comment"]
                    #next, we need to see the mode and flip the fields depending on who does what.
                    if activity == issue_constants.CASE_EVENT_ASSIGN:
                        issue.assigned_date = datetime.utcnow()
                        issue.assigned_by = request.current_actor
                        edit_comment += " (%s to %s by %s)" % (activity, issue.assigned_to.actordoc.get_name(), request.current_actor.actordoc.get_name())
                        
                    issue.save(request.current_actor, activity=activity, save_comment = edit_comment)
                    return HttpResponseRedirect(reverse('manage-issue', kwargs= {'issue_id': issue_id}))
            
            elif activity == issue_constants.CASE_EVENT_RESOLVE or activity == issue_constants.CASE_EVENT_CLOSE:
                form = IssueResolveCloseForm(data=request.POST, issue=theissue, activity=activity)
                context['form'] = form
                if form.is_valid():
                    status = form.cleaned_data['state']                    
                    comment = form.cleaned_data['comment']                    
                    theissue.status = status
                    theissue.last_edit_by = request.current_actor
                    
                    if activity == issue_constants.CASE_EVENT_CLOSE:
                        theissue.closed_by=request.current_actor
                    elif activity == issue_constants.CASE_EVENT_RESOLVE:
                        theissue.resolved_by=request.current_actor
        
                    theissue.save(request.current_actor, activity = activity, save_comment = comment)
                    
                    return HttpResponseRedirect(reverse('manage-issue', kwargs= {'issue_id': issue_id}))
            elif activity == issue_constants.CASE_EVENT_COMMENT:
                form = IssueCommentForm(data=request.POST)
                context['form'] = form
                if form.is_valid():
                    if form.cleaned_data.has_key('comment') and form.cleaned_data['comment'] != '':
                        comment = form.cleaned_data["comment"]
                    evt = IssueEvent()
                    evt.issue = theissue
                    evt.notes = comment
                    evt.activity = issue_constants.CASE_EVENT_COMMENT
                    evt.created_by = request.current_actor
                    evt.save()
                    return HttpResponseRedirect(reverse('manage-issue', kwargs= {'issue_id': issue_id}))
        else:
            #it's a GET
            issueform = None
            if activity==issue_constants.CASE_EVENT_EDIT or activity==issue_constants.CASE_EVENT_ASSIGN:
                issueform = IssueModelForm
            elif activity == issue_constants.CASE_EVENT_COMMENT:
                issueform = IssueCommentForm
            elif activity==issue_constants.CASE_EVENT_RESOLVE or activity==issue_constants.CASE_EVENT_CLOSE:
                issueform = IssueResolveCloseForm

            # This is a bit ugly at the moment as this view itself is the only place that instantiates the forms 
            if issueform == IssueModelForm:
                context['form'] = issueform(instance=theissue, editor_actor=request.current_actor, activity=activity)
                context['can_comment'] = False
            elif issueform == IssueResolveCloseForm:
                context['form'] = issueform(issue=theissue, activity=activity)
                context['can_comment'] = False                        
            elif issueform == IssueCommentForm:
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
    patients = Patient.objects.all()
    context = RequestContext(request)
    context['users'] = users
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

def actor_issues(request, actor_id, template_name="issuetracker/actor_issues.html"):
    context = RequestContext(request)
    actor=Actor.objects.get(id=actor_id)
    context['actor'] = actor
    #context['columns'] = ['description','last_edit_date', 'last_activity', 'last_edit_by_display']
    prop = request.GET.get('issuefilter', 'assigned_to')

    if prop == 'opened_by':
        context['issues'] = Issue.objects.filter(opened_by=actor)
    elif prop == 'assigned_to':
        context['issues'] = Issue.objects.filter(assigned_to=actor)

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
    issues = Issue.objects.filter(patient=patient).select_related('patient', 'last_edit_by')
    context['patient'] = patient
    context['issues'] = issues
    return render_to_response(template_name, context_instance=context)

