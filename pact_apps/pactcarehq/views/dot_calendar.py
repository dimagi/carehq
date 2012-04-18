from calendar import HTMLCalendar
from calendar import HTMLCalendar, month_name
from collections import defaultdict
from datetime import date
from django.core.urlresolvers import reverse
from django import forms
from django.forms.forms import Form
from pactpatient.enums import DAY_SLOTS_BY_IDX
import settings

class AggForm(Form):
    """
    """
    run_exclusions = forms.BooleanField()

    run_agechecker = forms.BooleanField()
    agechecker_days = forms.IntegerField(min_value=0, initial=365)

    run_prn_checker = forms.BooleanField()
    prn_checker_days = forms.IntegerField(min_value=0, initial=182)

    run_supply_checker = forms.BooleanField()
    supply_checker_days = forms.IntegerField(min_value=0, initial=182)

    run_supply_factor = forms.BooleanField()
    supply_factor = forms.CharField()

    run_latest_separation = forms.BooleanField()
    latest_separation = forms.IntegerField(min_value=0, initial=2)


    first_name = forms.CharField(required=True)
    middle_name = forms.CharField(required=False)
    last_name = forms.CharField(required=True)
    birthdate = forms.DateField(required=True)


def merge_dot_day(patient_doc, dots_observations):
    """
    Receive an array of CObservations and try to priority sort them and make a json-able array of ART and NON ART submissions
    for DOT calendar display AND ota restore.
    """
    day_dict = {'ART': {'total_doses':0, 'dose_dict': {} }, 'NONART': {'total_doses': 0, 'dose_dict': {}}}

    def cmp_observation(x, y):
        """
        for a given COBservation, do the following.
        If it's an addendump trumps all
        If it's direct, and other is not direct, direct wins
        If both direct, do by earliest date
        If neither direct, do by earliest date.
        < -1
        = 0
        > 1
        """
        #Reconcilation handling
        if getattr(x, 'is_reconciliation', False) and getattr(y, 'is_reconcilation', False):
            return cmp(x.submitted_date, y.submitted_date)
        elif getattr(x, 'is_reconciliation', False) and not getattr(y, 'is_reconcilation', False):
            return -1
        elif not getattr(x, 'is_reconciliation', False) and getattr(y, 'is_reconciliation', False):
            return 1

        if x.method == 'direct' and y.method == 'direct':
            return cmp(x.encounter_date, y.encounter_date)
        elif x.method == 'direct' and y.method != 'direct':
            return -1
        elif x.method != 'direct' and y.method == 'direct':
            return 1
        else:
            return cmp(x.encounter_date, y.encounter_date)



    for obs in dots_observations:
        if obs.is_art:
            dict_to_use = day_dict['ART']
        else:
            dict_to_use = day_dict['NONART']


        if dict_to_use['total_doses'] < obs.total_doses:
            dict_to_use['total_doses'] = obs.total_doses

        if dict_to_use['dose_dict'].get(obs.dose_number, None) is None:
            dict_to_use['dose_dict'][obs.dose_number] = []
        dict_to_use['dose_dict'][obs.dose_number].append(obs)

    for drug_type, wrapper_dict in day_dict.items():
        dose_dict = wrapper_dict['dose_dict']
        for dose_num in dose_dict.keys():
            observations = dose_dict[dose_num]
            observations = sorted(observations, cmp=cmp_observation, reverse=True) #key=lambda x: x.created_date, reverse=True)
            dose_dict[dose_num]=observations
        #wrapper_dict['dose_dict'] = dose_dict
    return day_dict


class DOTCalendar(HTMLCalendar):
    #source: http://journal.uggedal.com/creating-a-flexible-monthly-calendar-in-django/
    cssclasses = ["mon span2", "tue span2", "wed span2", "thu span2", "fri span2", "sat span2", "sun span2"]
    def __init__(self, patient_doc):
        super(DOTCalendar, self).__init__()
        #self.submissions = self.group_by_day(submissions)
        #self.django_patient = django_patient
        self.patient_doc = patient_doc

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

            day_submissions = self.patient_doc.dot_submissions_range(start_date=this_day, end_date=this_day)
            if len(day_submissions) > 0:
                cssclass += ' filled'
                body = ['<div class="calendar-cell">']
                day_data = merge_dot_day(self.patient_doc, day_submissions)

                for drug_type in day_data.keys():
                    body.append('')
                    body.append('<div class="drug-cell">')
                    body.append('<div class="drug-label">%s</div>' % drug_type)

                    drug_total = day_data[drug_type]['total_doses']

                    for dose_num, obs_list in day_data[drug_type]['dose_dict'].items():
                        for obs in obs_list:
                            if obs.day_slot != '' and obs.day_slot is not None:
                                day_slot_string = DAY_SLOTS_BY_IDX.get(int(obs.day_slot), 'Unknown')
                                body.append('<div class="time-label">%s</div>' % day_slot_string)
                            else:
                                body.append('<div class="time-label">Dose %d</div>' % (int(dose_num) + 1))
                            body.append('<div class="time-cell">')
                            body.append('<div class="observation">')
                            #body.append("%s,%s,%s,%s,%s,%s<br>" % (obs.encounter_date, obs.dose_number, obs.adherence, obs.method, obs.day_note, obs.day_slot))
                            if obs.adherence =='unchecked':
                                body.append('<span style="font-size:85%;color:#888;font-style:italic;">unchecked</span>')
                            else:
                                if obs.adherence == 'empty':
                                    body.append('<img src="%sdotsview/icons/check.jpg">' % settings.STATIC_URL)
                                elif obs.adherence == 'partial':
                                    body.append('<img src="%sdotsview/icons/exclamation-point.jpg">' % settings.STATIC_URL)
                                elif obs.adherence == 'full':
                                    body.append('<img src="%sdotsview/icons/x-mark.png">' % settings.STATIC_URL)

                                if obs.method == 'direct':
                                    body.append('<img src="%sdotsview/icons/plus.png">' % settings.STATIC_URL)
                                elif obs.method == 'pillbox':
                                    body.append('<img src="%sdotsview/icons/bucket.png">' % settings.STATIC_URL)
                                elif obs.method == 'self':
                                    body.append('<img src="%sdotsview/icons/minus.png">' % settings.STATIC_URL)

                            body.append('&nbsp;</div>')
                            break
                        body.append('&nbsp;</div>')
                    body.append('&nbsp;</div>')
                return self.day_cell(cssclass, '%d %s' % (day, ''.join(body)))

            if weekday < 5 and not future:
#                issue_check = Issue.objects.filter(patient=self.django_patient, due_date=datetime(this_day.year, this_day.month, this_day.day), category=get_missing_category())
                missing_link = []
#                if issue_check.count() == 0:
#                    #no issues resolving so completely missing
#
#                    missing_link.append('<div class="btn-group">')
#                    missing_link.append('<a class="btn btn-danger" href="#"><i class="icon-white icon-warning-sign"></i> Missing</a>')
#                    missing_link.append('<a class="btn btn-danger dropdown-toggle" data-toggle="dropdown" href="#"><span class="caret"></span></a>')
#                    missing_link.append('<ul class="dropdown-menu">')
#                    missing_link.append('<li><a href="%s?categoryid=%s&missing_date=%d-%d-%d">Create Issue</a></li>' % (reverse('new_carehq_patient_issue', kwargs={'patient_guid': self.django_patient.doc_id}), get_missing_category().id, this_day.year, this_day.month, this_day.day))
#                    missing_link.append('</ul>')
#                    missing_link.append('</div>')
#                else:
#                    missing_resolved=True
#                    still_open = issue_check.filter(status=ISSUE_STATE_OPEN)
#                    closed = issue_check.filter(status=ISSUE_STATE_CLOSED)
#                    missing_link.append('<div class="btn-group">')
#                    if still_open.count() == 0:
#                        missing_link.append('<a class="btn btn-info" href="#"><i class="icon-white icon-ok"></i> Closed</a>')
#                        missing_link.append('<a class="btn btn-info dropdown-toggle" data-toggle="dropdown" href="#"><span class="caret"></span></a>')
#                    else:
#                        missing_link.append('<a class="btn btn-warning" href="#"><i class="icon-white icon-edit"></i> Open</a>')
#                        missing_link.append('<a class="btn btn-warning dropdown-toggle" data-toggle="dropdown" href="#"><span class="caret"></span></a>')
#
#                    missing_link.append('<ul class="dropdown-menu">')
#                    if still_open.count() > 0:
#                        for i in still_open:
#                            missing_link.append('<li><a href="%s">View Issue</a></li>' % (reverse('manage-issue', kwargs={"issue_id": i.id})))
#                    else:
#                        for i in closed:
#                            missing_link.append('<li><a href="%s">View Issue</a></li>' % (reverse('manage-issue', kwargs={"issue_id": i.id})))
#
#                    missing_link.append('</ul>')
#                    missing_link.append('</div>')

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

