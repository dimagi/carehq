from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.safestring import mark_safe
from carehq_core import carehq_api
from couchforms.models import XFormInstance
from issuetracker.issue_constants import ISSUE_STATE_CLOSED
from issuetracker.models.issuecore import Issue
from patient.forms.address_form import SimpleAddressForm
from patient.forms.phone_form import PhoneForm
from patient.models import Patient
from patient.views import PatientSingleView
from permissions.models import Actor, PrincipalRoleRelation
from datetime import datetime, timedelta


from calendar import HTMLCalendar, month_name
from datetime import date
from itertools import groupby

from django.utils.html import conditional_escape as esc

class SubmissionCalendar(HTMLCalendar):
    #source: http://journal.uggedal.com/creating-a-flexible-monthly-calendar-in-django/
    cssclasses = ["mon span2", "tue span2", "wed span2", "thu span2", "fri span2", "sat span1", "sun span1"]
    def __init__(self, submissions):
        super(SubmissionCalendar, self).__init__()
        self.submissions = self.group_by_day(submissions)

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
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
            if date.today() < date(self.year, self.month, day):
                future=True
            else:
                future=False

            if day in self.submissions:
                cssclass += ' filled'
                body = ['<br>']
                day_submissions = self.submissions[day]
                body.append('<a href="#" class="btn btn-success">')
                body.append("Received")
                if len(day_submissions) > 1:
                    body.append(" (%d)" % len(day_submissions))
                body.append('</a>')
                body.append('<br>')
                return self.day_cell(cssclass, '%d %s' % (day, ''.join(body)))

            if weekday < 5 and not future:
                missing_link = '<br><a href="#" class="btn btn-warning">Missing</a><br>'
                return self.day_cell(cssclass, "%d %s" % (day, missing_link))
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
        context['view_mode'] = view_mode
        context['is_me'] = is_me
        pdoc = context['patient_doc']
        dj_patient = context['patient_django']

        if view_mode == 'issues':
            context['filter'] = request.GET.get('filter', 'recent')
            issues = Issue.objects.filter(patient=dj_patient)
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
            sk = ['Test000001', viewyear, viewmonth, 0]
            ek = ['Test000001', viewyear, viewmonth, 31]

            submissions = XFormInstance.view('carehqapp/ccd_submits_by_patient_doc', startkey=sk, endkey=ek, include_docs=True).all()
#            submissions = []
            cal = SubmissionCalendar(submissions).formatmonth(viewyear, viewmonth)
            context['calendar'] = mark_safe(cal)
            self.template_name = "carehqapp/patient/carehq_patient_submissions.html"


        return context
        #return render_to_response(template_name, context_instance=context)

