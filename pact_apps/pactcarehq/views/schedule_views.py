from datetime import datetime, timedelta
import hashlib
import uuid
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import cache, simplejson
from django.views.decorators.cache import cache_page
from couchforms.models import XFormInstance
from pactcarehq import schedule
from pactcarehq.views import DAYS_OF_WEEK
from pactcarehq.views.patient_views import getpatient
from pactpatient.models import CDotWeeklySchedule
from patient.models import Patient


def _get_schedule_tally(username, total_interval, override_date=None):
    """
    For a given username and interval, get a simple array of the username and scheduled visit (whether a submission is there or not)  exists.
    returns (schedule_tally_array, patient_array, total_scheduled (int), total_visited(int))
    schedul_tally_array = [visit_date, [(patient1, visit1), (patient2, visit2), (patient3, None), (patient4, visit4), ...]]
    where visit = XFormInstance
    """
    if override_date == None:
        nowdate = datetime.now()
        chw_schedule = schedule.get_schedule(username)
    else:
        nowdate = override_date
        chw_schedule = schedule.get_schedule(username, override_date = nowdate)
    #got the chw schedule
    #now let's walk through the date range, and get the scheduled CHWs per this date.visit_dates = []
    ret = [] #where it's going to be an array of tuples:
    #(date, scheduled[], submissions[] - that line up with the scheduled)

    total_scheduled=0
    total_visited=0

    for n in range(0, total_interval):
        td = timedelta(days=n)
        visit_date = nowdate-td
        scheduled_pactids = chw_schedule.get_scheduled(visit_date)
        patients = []
        visited = []
        for pact_id in scheduled_pactids:
            if pact_id == None:
                continue
            try:
                total_scheduled += 1
                cpatient = getpatient(pact_id) #TODO: this is a total waste of queries, doubly getting the cpatient, then getting the django object again
#                patients.append(Patient.objects.get(id=cpatient.django_uuid))
                patients.append(cpatient)
            except:
                continue

        #inefficient, but we need to get the patients in alpha order
        patients = sorted(patients, key=lambda x: x.last_name)
        for patient in patients:
            pact_id = patient.pact_id
            searchkey = [str(username), str(pact_id), visit_date.year, visit_date.month, visit_date.day]
            submissions = XFormInstance.view('pactcarehq/submits_by_chw_per_patient_date', key=searchkey, include_docs=True).all()
            if len(submissions) > 0:
                visited.append(submissions[0])
                total_visited+= 1
            else:
                #ok, so no submission from this chw, let's see if there's ANY from anyone on this day.
                other_submissions = XFormInstance.view('pactcarehq/all_submits_by_patient_date', key=[str(pact_id), visit_date.year, visit_date.month, visit_date.day, 'http://dev.commcarehq.org/pact/dots_form' ], include_docs=True).all()
                if len(other_submissions) > 0:
                    visited.append(other_submissions[0])
                    total_visited+= 1
                else:
                    visited.append(None)

        ret.append((visit_date, zip(patients, visited)))
    return ret, patients, total_scheduled, total_visited



@login_required
def chw_calendar_submit_report_all(request):
    from pactcarehq.tasks import all_chw_submit_report
    download_id = uuid.uuid4().hex
    total_interval = 7
    if request.GET.has_key('interval'):
        try:
            total_interval = request.GET['interval']
            if total_interval == "all":
                total_interval = 1000
            else:
                total_interval = int(total_interval)
        except:
            pass
    all_chw_submit_report.delay(total_interval, download_id)
    return HttpResponseRedirect(reverse('retrieve_download', kwargs={'download_id': download_id}))

@login_required
def chw_calendar_submit_report(request, username, template_name="pactcarehq/chw_calendar_submit_report.html"):
    """Calendar view of submissions by CHW, overlaid with their scheduled visits, and whether they made them or not."""
    context = RequestContext(request)
    all_patients = request.GET.get("all_patients", False)
    context['username'] = username
    user = User.objects.get(username=username)
    total_interval = 7
    if request.GET.has_key('interval'):
        try:
            total_interval = int(request.GET['interval'])
        except:
            pass

    ret, patients, total_scheduled, total_visited= _get_schedule_tally(username, total_interval)
    nowdate = datetime.now()

    context['date_arr'] = ret
    context['total_scheduled'] = total_scheduled
    context['total_visited'] = total_visited
    #context['total_visited'] = total_visited
    context['start_date'] = ret[0][0]
    context['end_date'] = ret[-1][0]


    if request.GET.get('getcsv', None) != None:
        csvdata = []
        csvdata.append(','.join(['visit_date','assigned_chw','pact_id','is_scheduled','contact_type', 'visit_type','visit_kept', 'submitted_by','visit_id']))
        for date, pt_visit in ret:
            if len(pt_visit) > 0:
                for cpt, v in pt_visit:
                    rowdata = [date.strftime('%Y-%m-%d'), username, cpt.pact_id]
                    if v != None:

                        #is scheduled
                        if v.form['scheduled'] == 'yes':
                            rowdata.append('scheduled')
                        else:
                            rowdata.append('unscheduled')
                        #contact_type
                        rowdata.append(v.form['contact_type'])

                        #visit type
                        rowdata.append(v.form['visit_type'])

                        #visit kept
                        rowdata.append(v.form['visit_kept'])

                        rowdata.append(v.form['Meta']['username'])
                        if v.form['Meta']['username'] == username:
                            rowdata.append('assigned')
                        else:
                            rowdata.append('covered')
                        rowdata.append(v.get_id)
                    else:
                        rowdata.append('novisit')
                    csvdata.append(','.join(rowdata))
            else:
                csvdata.append(','.join([date.strftime('%Y-%m-%d'),'nopatients']))

        resp = HttpResponse()

        resp['Content-Disposition'] = 'attachment; filename=chw_schedule_%s-%s_to_%s.csv' % (username, datetime.now().strftime("%Y-%m-%d"),  (nowdate - timedelta(days=total_interval)).strftime("%Y-%m-%d"))
        resp.write('\n'.join(csvdata))
        return resp

    else:
        return render_to_response(template_name, context_instance=context)



def _get_submissions_for_patient_by_date(patient, visit_dates, schema='http://dev.commcarehq.org/pact/dots_form'):
    """Argument: Patient django object, visit date
    Will return a view result of all submissions by patient where the key is the patient pact_id
    return value: [pact_id, year, month, day]=>submission"""

    keys = []
    date_key_map = {}
    #t2 = datetime.now()
    for visit_date in visit_dates:
        day_of_week = visit_date.isoweekday()-1
        yearstart = visit_date.year
        monthstart = visit_date.month
        datestart = visit_date.day
        #get the xform count for that day
        key = [patient.couchdoc.pact_id, yearstart, monthstart, datestart, schema]
        keys.append(key)
        key_str = ''.join([str(x) for x in key])
        date_key_map[key_str] = visit_date
    submit_reduction = XFormInstance.view('pactcarehq/all_submits_by_patient_date', keys=keys)
    #d2 = datetime.now()-t2
    #print "\tSingle Patient data query QUERY: %d.%d" % (d2.seconds, d2.microseconds/1000)
    #t3 = datetime.now()
    ret = {} #a return value of date ordered submissions by
    for row in submit_reduction:
        key = row['key']
        key_str = ''.join([str(x) for x in key])
        submits = row['value']

        date = date_key_map[key_str]
        ret[date] = [XFormInstance.wrap(x) for x in submits]
    #d3 = datetime.now()-t3

    #print "\tSingle Patient data query HASHING: %d.%d" % (d3.seconds, d3.microseconds/1000)

    return ret


def _get_scheduled_chw_for_patient_visit(patient, visit_date):

    """Get the active scheduled chw for that day.
    returns a string of the chw username"""
    key = patient.couchdoc.pact_id
    visit_schedule_cache_key = hashlib.md5('patient_visit_schedule-%s-%s' % (key, visit_date.strftime("%Y-%m-%d"))).hexdigest()

    ####
    #Step 1, see if this has been cached before for that given chw
    chw_scheduled = cache.get(visit_schedule_cache_key, None)
    if chw_scheduled != None:
        #print "cache hit! %s on %s-%s" % (chw_scheduled, key, visit_date.strftime("%Y-%m-%d"))
        return chw_scheduled

    ################################
    #Step 2, get the patient's entire visit schedule, cache the whole thing

    pt_schedule_cache_key = 'patient_schedule_key-%s' % (patient.couchdoc.pact_id)
    sched_dicts = cache.get(pt_schedule_cache_key, None)
    if sched_dicts == None:
        reduction = CDotWeeklySchedule.view('pactcarehq/patient_dots_schedule', key=key).first()
        if reduction == None:
            cache.set(pt_schedule_cache_key, repr({}))
            sched_dicts = {}
        else:
            sched_dicts = reduction['value']
        sched_dicts = sorted(sched_dicts, key=lambda x: x['started'])

        cache.set(pt_schedule_cache_key, simplejson.dumps(sched_dicts))
    else:
        sched_dicts = simplejson.loads(sched_dicts)

    ######
    #Step 3
    #having received the schedule dictionary, now process the scheduled chw for that visit date
    used_schedule=None
    chw_scheduled = None
    day_of_week = visit_date.isoweekday() %7 #isoweekday is monday 1, sunday 7, mod 7 to make sunday 0
    for sched_dict in sched_dicts:
        sched = CDotWeeklySchedule.wrap(sched_dict)
        if (sched.ended == None or sched.ended > visit_date) and sched.started <= visit_date:
            used_schedule=sched
    if used_schedule != None:
        day_string = DAYS_OF_WEEK[day_of_week]
        chw_scheduled = used_schedule[day_string]
    cache.set(visit_schedule_cache_key, str(chw_scheduled))
    #print "setting cache: %s for %s-%s" %(chw_scheduled, key, visit_date.strftime("%Y-%m-%d"))

    return chw_scheduled




@login_required
@cache_page(60 * 5)
def patient_schedule_report(request, patient_id, template_name="pactcarehq/patient_calendar_submit_report.html"):
    """returns a view of the patient's scheduled visits for a given date (which chw it should have been), as well as the visit if there was one
    returns an acheduled_item, ...], [submissions], ...]
    """
    context = RequestContext(request)
    pt = Patient.objects.get(id=patient_id)

    total_interval = 7
    if request.GET.has_key('interval'):
        try:
            total_interval = request.GET['interval']
            if total_interval == "all":
                total_interval = 1000
            else:
                total_interval = int(total_interval)
        except:
            pass


    ret = []
    context['patient'] = pt

    visit_dates = []
    scheduled_by_date = {}
    for n in range(0, total_interval):
        td = timedelta(days=n)
        visit_date = datetime.utcnow()-td
        visit_dates.append(visit_date)

    submits_per_date = _get_submissions_for_patient_by_date(pt, visit_dates)
    for visit_date in visit_dates:
        if submits_per_date.has_key(visit_date):
            submits = submits_per_date[visit_date]
        else:
            submits = []
        #scheduled = scheduled_by_date[visit_date]
        scheduled_chw = _get_scheduled_chw_for_patient_visit(pt, visit_date)
        ret.append([visit_date, [scheduled_chw], submits])
    context['date_arr'] = ret
    return render_to_response(template_name, context_instance=context)
