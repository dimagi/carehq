from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import  RequestContext
from django.contrib.auth.decorators import login_required
from dimagi.utils.make_time import make_time
from issuetracker.forms import NewIssueForm
from issuetracker.issue_constants import CASE_STATE_OPEN, CASE_EVENT_OPEN
from lib.crumbs import crumbs
from patient.models.patientmodels import SimplePatient

def my_issues_patient(request, template_name = "carehqapp/my_issues_patient.html"):
    context = RequestContext(request)
    user = request.user
    context['user'] = user
    return render_to_response(template_name, context_instance=context)

def my_issues_caregiver(request, template_name = 'carehqapp/my_issues_caregiver.html'):
    context = RequestContext(request)
    user = request.user
    context['user'] = user
    return render_to_response(template_name, context_instance=context)

def my_issues_provider(request, template_name = 'carehqapp/my_cases_provider.html'):
    context = RequestContext(request)
    user = request.user
    context['user'] = user
    return render_to_response(template_name, context_instance=context)

def issues_patient(request, patient_id, template_name='carehqapp/issues_patient.html'):
    context = RequestContext(request)
    user = request.user
    context['user'] = user
    return render_to_response(template_name, context_instance=context)


@login_required
def new_issue_patient(request, patient_guid, template_name="carehqapp/activities/issue/new_issue.html"):
    context = RequestContext(request)
    patient_doc = SimplePatient.get(patient_guid)
    if request.method == "POST":
        form = NewIssueForm(patient_doc, request.current_actor, data=request.POST)
        if form.is_valid():
            newissue = form.save(commit=False)
            newissue.last_edit_by = request.current_actor
            newissue.last_edit_date = make_time()
            newissue.patient = patient_doc.django_patient
            newissue.opened_by=request.current_actor
            newissue.opened_date = make_time()
            newissue.status = CASE_STATE_OPEN
            newissue.save(request.current_actor, activity=CASE_EVENT_OPEN)
            return HttpResponseRedirect(patient_doc.get_absolute_url())
    else:
        context['form'] = NewIssueForm(patient_doc.django_patient, request.current_actor)
    return render_to_response(template_name, context_instance=context)

@crumbs("Issue List", "issue_home", "my_profile")
@login_required
def issue_home(request, template_name="carehqapp/issue_home.html"):
#    request.breadcrumbs("Issue List", reverse(issue_home))
    context = RequestContext(request)
    user = request.user
    return render_to_response(template_name, context_instance=context)
#
#    ########################
#    #get the logged in user's filter profile, if the profile doesn't exist, make a new FilterProfile and arbitrarily use the first case filter
#    # if it does exist, load up the last filter used, OR whatever the query string is saying it is.
#    display_filter = None
#
#    request.session['is_listing'] = 'something'
#    request.session['is_whatever'] = 'askldjqwoerwqer'
#    request.session.modified=True
##    try:
##        profile = FilterProfile.objects.get(user = user)
##    except ObjectDoesNotExist:
##        #make the new case profile
##        profile = FilterProfile()
##        profile.user = user
##        profile.filter = Filter.objects.all()[0]
##        profile.last_filter = Filter.objects.all()[0] #this is a nasty hack, as we're assuming id 1 is the reflexive one
#
#    display_filter = Filter.objects.all()[1]
#
#
#    group_by_col = None
#
#    if 'filter' in request.GET:
#        filter_id = request.GET['filter']
#        display_filter = Filter.objects.get(id=filter_id)
##    else:
##        display_filter = profile.last_filter
#    group_by_col = request.GET.get('groupBy', None)
#
#
#    #profile.last_login = datetime.utcnow()
#    #profile.last_login_from = request.META['REMOTE_ADDR']
#    #profile.last_filter = display_filter
#    #profile.save()
#
#    split_headings = False
#    qset = display_filter.get_filter_queryset()
#
#    if group_by_col and group_by_col.count('_date') > 0:
#        split_headings = False
#        qset.order_by(group_by_col)
#    elif group_by_col == 'description':
#        split_headings = False
#        qset.order_by('description')
#    elif  group_by_col == 'assigned_to' or group_by_col == 'closed_by' or group_by_col == 'opened_by'\
#        or group_by_col == 'last_edit_by' or group_by_col == 'resolved_by' or group_by_col == 'last_event_by':
#        model_class = User
#        split_headings = True
#    elif group_by_col == 'patient':
#        model_class = Patient
#        split_headings = True
#    elif group_by_col == 'status':
#        model_class = Status
#        split_headings = True
#    elif group_by_col == 'priority':
#        model_class = Priority
#        split_headings = True
#    elif group_by_col == 'category':
#        model_class = Issue
#        split_headings = True
#
#    qset_dict = {}
#
#    #If we are splitting the queryset up by the sorting category,
#    #we need to iterate over the distinct objects in the model class
#    if split_headings:
#        heading_keys = model_class.objects.all().distinct() #This is a bit inefficient as it does it over all the
#        for key in heading_keys:
#            #http://www.nomadjourney.com/2009/04/dynamic-django-queries-with-kwargs/
#            #dynamic django queries baby
#            if group_by_col == 'patient':
#                subq = qset.filter(patient=key)
#            else:
#                kwargs = {str(group_by_col +"__id__endswith"): str(key.id), }
#                subq = qset.filter(**kwargs)
#            if subq.count() > 0:
#                qset_dict[key] = subq
#    else:
#        qset_dict[display_filter.description] = qset
#
#
#    context['qset_dict'] = qset_dict
#    #context['profile'] = profile
#    context['filter'] = display_filter
#    #context['filter_cases'] = display_filter.get_filter_queryset()
#    context['gridpreference'] = context['filter'].gridpreference
#    ############################
#
#    filter_columns = display_filter.gridpreference.get_display_columns.values_list('column__name', flat=True)
#    context['columns'] = display_filter.gridpreference.get_display_columns
#
#
#    return render_to_response(template_name, context, context_instance=RequestContext(request))




