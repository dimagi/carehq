from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from carehq_core import carehq_api
from carehqapp.models import CCDSubmission, get_missing_category
from issuetracker.issue_constants import ISSUE_STATE_CLOSED, ISSUE_STATE_OPEN
from issuetracker.models.issuecore import Issue
from patient.views import PatientSingleView
from datetime import datetime

from clinical_shared.decorators import actor_required

from calendar import HTMLCalendar, month_name
from datetime import date
from itertools import groupby

class SubmissionCalendar(HTMLCalendar):
    #source: http://journal.uggedal.com/creating-a-flexible-monthly-calendar-in-django/
    cssclasses = ["mon span2", "tue span2", "wed span2", "thu span2", "fri span2", "sat span1", "sun span1"]
    def __init__(self, submissions, django_patient):
        super(SubmissionCalendar, self).__init__()
        self.submissions = self.group_by_day(submissions)
        self.django_patient = django_patient

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        #make sure to roll over year?
        nextyear=theyear
        prevyear=theyear
        if themonth + 1 > 12:
            nextmonth=1
            nextyear=theyear+1
        else:
            nextmonth=themonth+1
        if themonth-1 == 0:
            prevmonth = 12
            prevyear=theyear-1
        else:
            prevmonth=themonth-1

        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        ret = []
        a = ret.append
        a('<tr>')
        a('<th colspan="7" class="month" style="text-align:center;">')
        a('<ul class="pager">')
        a('<li class="previous"><a href="?month=%d&year=%d">Previous</a></li>' % (prevmonth, prevyear))
        a('<li class="disabled">')
        a(s)
        a('</li>')
        a('<li class="next"><a href="?month=%d&year=%d">Next</a></li>' % (nextmonth, nextyear))
        a('</ul>')
        a('</th>')
        a('</tr>')
        return ''.join(ret)
        #return '<tr><th colspan="7" class="month">%s</th></tr>' % s


    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            this_day = date(self.year, self.month, day)
            if date.today() == this_day:
                cssclass += ' today'
            if date.today() < this_day:
                future=True
            else:
                future=False

            if day in self.submissions:
                cssclass += ' filled'
                body = ['<br>']

                #received
                day_submissions = sorted(self.submissions[day], key=lambda x: x.get_session_time())
                threshold_resolved=True
                treshold_body = []

#                body.append('<ul class="nav">')
#                body.append('<li class="dropdown">')
#                body.append('<a class="dropdown-toggle label label-info" data-toggle="dropdown" href="#">Received')
#                body.append(' <b class="caret"></b></a>')
#                body.append('<ul class="dropdown-menu">')

                body.append('<div class="btn-group">')
                body.append('<a class="btn btn-info" href="#"><i class="icon white user"></i> Received</a>')
                body.append('<a class="btn btn-info dropdown-toggle" data-toggle="dropdown" href="#"><span class="caret"></span></a>')
                body.append('<ul class="dropdown-menu">')

                for submit in day_submissions:
                    if submit.is_threshold:
                        #ok, it's a threshold violation, let's check if the issue is closed
                        issues = submit.get_issues()
                        for issue in issues:
                            if issue.is_closed:
                                treshold_body.append('<li><a href="%s">%s Closed</a></li>' % (reverse('manage-issue', kwargs={"issue_id": issue.id}), submit.get_session_time().strftime("%I:%M%p")))
                            else:
                                threshold_resolved=False
                                treshold_body.append('<li><a href="%s">%s Open</a></li>' % (reverse('manage-issue', kwargs={"issue_id": issue.id}), submit.get_session_time().strftime("%I:%M%p")))
                    else:
                        #it's not a threshold violation, get "OK" submits
#                        body.append('<li><a href="#"><i class="icon-ok"></ia> OK</a></li>')
                        body.append('<li><a href="%s"> %s OK</a></li>' % (reverse('view_ccd', kwargs={'doc_id': submit._id}), submit.get_session_time().strftime('%I:%M%p')))
                                    #(reverse('new_carehq_patient_issue', kwargs={'patient_guid': self.django_patient.doc_id}), get_missing_category().id, this_day.year, this_day.month, this_day.day))
                body.append('</ul>')
                body.append('</div>')


                if threshold_resolved:
                    #body.append('<a href="" class="label label-success">OK</a><br>')
                    #link to resolved issues
                    pass
                else:
                    body.append('<span class="label label-important">Received</span><br>')
                    body.append(''.join(treshold_body))
                body.append('<br>')
                return self.day_cell(cssclass, '%d %s' % (day, ''.join(body)))

            if weekday < 5 and not future:
                issue_check = Issue.objects.filter(patient=self.django_patient, due_date=datetime(this_day.year, this_day.month, this_day.day), category=get_missing_category())
                missing_link = []
                if issue_check.count() == 0:
                    #no issues resolving so completely missing

                    missing_link.append('<div class="btn-group">')
                    missing_link.append('<a class="btn btn-warning" href="#"><i class="icon white user"></i> Missing</a>')
                    missing_link.append('<a class="btn btn-warning dropdown-toggle" data-toggle="dropdown" href="#"><span class="caret"></span></a>')
                    missing_link.append('<ul class="dropdown-menu">')
                    missing_link.append('<li><a href="%s?categoryid=%s&missing_date=%d-%d-%d">Create Issue</a></li>' % (reverse('new_carehq_patient_issue', kwargs={'patient_guid': self.django_patient.doc_id}), get_missing_category().id, this_day.year, this_day.month, this_day.day))
                    missing_link.append('</ul>')
                    missing_link.append('</div>')
                else:
                    missing_resolved=True
                    still_open = issue_check.filter(status=ISSUE_STATE_OPEN)
                    missing_link.append('<div class="btn-group">')
                    if still_open.count() == 0:
                        missing_link = '<br><span class="label label-info">Missing - Closed</span>'
                    else:
                        missing_link = '<br><span class="label label-warning">Missing - Active</span><br>'
                    if still_open.count() == 0:
                        missing_link.append('<a class="btn btn-info" href="#"><i class="icon white user"></i> Missing - Closed</a>')
                    else:
                        missing_link.append('<a class="btn btn-warning" href="#"><i class="icon white user"></i> Missing - Open</a>')

                    missing_link.append('<a class="btn btn-warning dropdown-toggle" data-toggle="dropdown" href="#"><span class="caret"></span></a>')
                    missing_link.append('<ul class="dropdown-menu">')
                    for i in still_open:
                        missing_link.append('<li><a href="%s">View Issue</a></li>' % (reverse('manage-issue', kwargs={"issue_id": i.id})))
                    missing_link.append('</ul>')
                    #missing_link = '<br><span class="label label-warning">Missing</span><br>'
                    #missing_link += '<a href="%s?categoryid=%s&missing_date=%d-%d-%d">Create Issue</a>' % (reverse('new_carehq_patient_issue', kwargs={'patient_guid': self.django_patient.doc_id}), get_missing_category().id, this_day.year, this_day.month, this_day.day)
                    missing_link.append('</div>')

                return self.day_cell(cssclass, "%d %s" % (day, ''.join(missing_link)))
            elif weekday < 5 and future:
                return self.day_cell('future', "%d" % day)
            else:
                return self.day_cell(cssclass, day)
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """
        self.year, self.month = theyear, themonth
        #return super(SubmissionCalendar, self).formatmonth(year, month)
        #rather than do super, do some custom css trickery
        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="table table-bordered">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)

    def group_by_day(self, submissions):
        field = lambda submission: datetime.strptime(submission.form['author']['time']['@value'][0:8], '%Y%m%d').day
        return dict(
            [(day, list(items)) for day, items in groupby(submissions, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)


class CarehqPatientSingleView(PatientSingleView):
    #template carehqapp/carehq_patient_base.html

    def get_context_data(self, **kwargs):
        """
        Main patient view for pact.  This is a "do lots in one view" thing that probably shouldn't be replicated in future iterations.
        """
        request = self.request

        #hack to check for actor since I can't seem to get the decorators to work
        if not hasattr(request, 'current_actor') or request.current_actor is None:
            raise PermissionDenied
            #return HttpResponseRedirect(reverse('no_actor_profile'))

        schedule_show = request.GET.get("schedule", "active")
        schedule_edit = request.GET.get("edit_schedule", False)
        address_edit = request.GET.get("edit_address", False)
        address_edit_id = request.GET.get("address_id", None)
        new_address = True if request.GET.get("new_address", False) == "True" else False
        phone_edit = request.GET.get("edit_phone", False)
        patient_edit = request.GET.get('edit_patient', None)
        show_all_schedule = request.GET.get('allschedules', None)

        is_me=False
        patient_guid = self.kwargs.get('patient_guid', None)

        if patient_guid is None:
            #verify that this is the patient itself.
            if request.current_actor.is_patient:
                patient_guid = request.current_actor.actordoc.patient_doc_id
                kwargs['patient_guid'] = patient_guid
                is_me=True
            else:
                raise Http404


        #global info
        view_mode = self.kwargs.get('view_mode', '')
        if view_mode == '':
            view_mode = 'info'
        context = super(CarehqPatientSingleView, self).get_context_data(**kwargs)

        if not carehq_api.has_permission(request.current_actor.actordoc, context['patient_doc']) and not request.user.is_superuser:
            raise PermissionDenied

        context['view_mode'] = view_mode
        context['is_me'] = is_me
        pdoc = context['patient_doc']
        dj_patient = context['patient_django']

        if view_mode == 'issues':
            context['filter'] = request.GET.get('filter', 'recent')
            issues = Issue.objects.filter(patient=dj_patient)
            foo
            if context['filter']== 'closed':
                issues = issues.filter(status=ISSUE_STATE_CLOSED)
            elif context['filter'] == 'recent':
                issues = issues.order_by('-last_edit_date')
            elif context['filter'] == 'open':
                issues = issues.exclude(status=ISSUE_STATE_CLOSED)

            context['issues'] = issues
            self.template_name = "carehqapp/patient/carehq_patient_issues.html"
        if view_mode == 'info':
            self.template_name = "carehqapp/patient/carehq_patient_info.html"

        if view_mode == 'careteam':
            context['patient_careteam'] = carehq_api.get_careteam(pdoc)
            self.template_name = "carehqapp/patient/carehq_patient_careteam.html"

        if view_mode == 'careplan':
            self.template_name = "carehqapp/patient/carehq_patient_careplan.html"

        if view_mode == 'submissions':
            viewmonth = int(request.GET.get('month', date.today().month))
            viewyear = int(request.GET.get('year', date.today().year))
            sk = [pdoc.study_id, viewyear, viewmonth, 0]
            ek = [pdoc.study_id, viewyear, viewmonth, 31]

            submissions = CCDSubmission.view('carehqapp/ccd_submits_by_patient_doc', startkey=sk, endkey=ek, include_docs=True).all()
#            submissions = []
            cal = SubmissionCalendar(submissions, dj_patient).formatmonth(viewyear, viewmonth)
            context['calendar'] = mark_safe(cal)
            self.template_name = "carehqapp/patient/carehq_patient_submissions.html"


        return context
        #return render_to_response(template_name, context_instance=context)

