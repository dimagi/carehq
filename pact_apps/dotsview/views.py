from StringIO import StringIO
import logging
import os
import uuid
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template.context import Context, Context
from dimagi.utils.couch.database import get_db
from dotsview.forms import AddendumForm

from models import *
from django.contrib.auth.decorators import login_required
from patient.models.couchmodels import CPatient
from couchforms.models import XFormInstance
from patient.models.couchmodels import ghetto_regimen_map
from django.forms.formsets import formset_factory
from django.core.cache import cache
from dotsview.tasks import csv_export
from datetime import datetime, timedelta
import csv



def _parse_date(string):
    if isinstance(string, basestring):
        return datetime.strptime(string, "%Y-%m-%d").date()
    else:
        return string


@login_required
def get_csv(request):
    download_id = uuid.uuid1().hex

    csv_mode = request.GET.get('csv', None)
    end_date = _parse_date(request.GET.get('end', datetime.utcnow()))
    start_date = _parse_date(request.GET.get('start', end_date - timedelta(30)))
    patient_id = request.GET.get('patient', None)

    csv_export.delay(csv_mode, end_date.strftime('%Y-%m-%d'), start_date.strftime('%Y-%m-%d'), patient_id, download_id)
    return HttpResponseRedirect(reverse('pactcarehq.views.file_download', kwargs={'download_id': download_id}))
    #return HttpResponse('<html><body>Task for csv download generated<br><br><a href="%s">Download Link</a></body></html>' % (reverse('dotsview.views.file_download', kwargs={'download_id':download_id})))



def delete_reconciliation(request):
    print "entering delete reconciliation"
    if request.method == "POST":
        try:
            doc_id = request.POST['doc_id']
            db = get_db()
            print "does doc exist"
            if db.doc_exist(doc_id):
                print "trying to get doc id"
                doc = db.open_doc(doc_id)
                print "got doc id"
                if doc['doc_type'] == "CObservationAddendum":
                    print "trying to delete"
                    db.delete_doc(doc)
                    print "able to delete"
                    return HttpResponse("Success")
                else:
                    print "wtf, not an Cobservation?"
                    raise
        except Exception, e:
            print "huh, weird"
            logging.error("Error getting args:" + str(e))
            return HttpResponse("Error")
    else:
        raise Http404


artkeys = ('ART', 'Non ART')
def _get_observations_for_date(date, pact_id, art_num, nonart_num, reconcile_trump=False):
    """Returns a table showing the conflicts for a given date submission.
    """
    grouping = {}
    day_notes = []
    conflict_dict = {} # k, v = doc_id =>
    conflict_check = {} # k,v = (drug_type, dose_number, dose_total) => observation
    datekey = [pact_id, 'observe_date', date.year, date.month, date.day]
    observations = CObservation.view('pactcarehq/dots_observations', key=datekey).all()
    total_doses_set = set([obs.total_doses for obs in observations])

    has_reconciled = False
    #prep the groupings
    # grouping[art | nonart] => times[morning | noon | etc] = [observations] - if there are multiple then there are multiple
    for artkey in artkeys:
        grouping[artkey] = {}

    for ob in observations:
        #base case if it's never been seen before, add it as the key
        if not conflict_check.has_key(ob.adinfo[0]):
            conflict_check[ob.adinfo[0]] = ob

        #main check.  for the given key adinfo[0], check to see if the value is identical
        prior_ob = conflict_check[ob.adinfo[0]]
        if prior_ob.adinfo[1] != ob.adinfo[1]:
            #they don't match, add the current ob to the conflict dictionary
            if not conflict_dict.has_key(ob.doc_id):
                conflict_dict[ob.doc_id] = ob
                #next, add the one existing in the lookup checker as well because they differed.
            if not conflict_dict.has_key(prior_ob.doc_id):
                conflict_dict[prior_ob.doc_id] = prior_ob
        if ob.is_reconciliation:
            #it's a reconciled entry
            has_reconciled = True

        try:
            time_label = ob.get_time_label()
        except IndexError:
            logging.error("Error, observation time label index not found, DOT data generation error")
#            hack_patient = CPatient.view('patient/pact_ids', key=pact_id, include_docs=True).first()
#            if ob.is_art:
#                total_doses = hack_patient.art_num
#            else:
#                total_doses = hack_patient.non_art_num
            time_label = TIME_LABELS[ob.dose_number]

        if time_label != "":
            if not grouping['ART' if ob.is_art else 'Non ART'].has_key(time_label):
                grouping['ART' if ob.is_art else 'Non ART'][time_label] = []

            if ob.is_reconciliation and reconcile_trump==True:
                grouping['ART' if ob.is_art else 'Non ART'][time_label] = [ob]
                logging.error("reconciled entry, droping all others for time label")
            else:
                grouping['ART' if ob.is_art else 'Non ART'][time_label].append(ob)

        else:
            logging.error("Error Doc: %s - Time label not retrievable due to regimen count error" % (ob.doc_id))
            logging.error("Day Index: %s, Dose Number: %d, Total Doses: %d" % (ob.day_index, ob.dose_number, ob.total_doses))

    #for each class of drug (art, non art) in artkeys
    #for each time in the timeslots (morning, afternoon, etc)
    #get the most recent observation for that time slot observed_date[-1:] - make it a list because we iterate through them
    #return ([(ak, [(tk, sorted(grouping[ak][tk], key=lambda x: x.observed_date)[-1:]) for tk in timekeys]) for ak in artkeys], conflict_dict.values(), day_notes)

    #sort the groupings by reverse date order
    if has_reconciled:
        data_sort_reverse = False
    else:
        data_sort_reverse = True
    for drugtype, timelabel_dict in grouping.items():
        for time_label in timelabel_dict.keys():
            timelabel_dict[time_label] = sorted(set(timelabel_dict[time_label]), key=lambda x: x.anchor_date,
                                                reverse=data_sort_reverse)

    return (grouping, has_reconciled)

@login_required
def dot_addendum(request, template='dots/dot_addendum.html'):
    #get stuff from the GET
    context = RequestContext(request)
    #todo: we need to make a checksum for these POSTs

    #step 1, basic prep
    if request.method == "GET":
        patient_id = request.GET.get('patient', None)
        addendum_date = datetime.strptime(request.GET.get('addendum_date', None), "%Y-%m-%d")
    elif request.method == "POST":
        patient_id = request.POST['patient_id']
        addendum_date = datetime.strptime(request.POST['addendum_date'], "%Y-%m-%d")

    patient = Patient.objects.get(id=patient_id)
    pact_id = patient.couchdoc.pact_id
    art_regimen = patient.couchdoc.art_regimen
    art_num = int(ghetto_regimen_map[art_regimen.lower()])

    nonart_regimen = patient.couchdoc.non_art_regimen
    nonart_num = int(ghetto_regimen_map[nonart_regimen.lower()])

    context['art_forms'] = []
    context['nonart_forms'] = []
    AddendumFormSetFactory = formset_factory(AddendumForm, extra=nonart_num + art_num, max_num=nonart_num + art_num)
    if request.method == "POST":
        formset = AddendumFormSetFactory(request.POST, request.FILES)
        if formset.is_valid():
            #iterate through all the forms in the formset, create CObservation and put it into CObservationAddendum
            addendum = CObservationAddendum()
            addendum._id = uuid.uuid1().hex
            addendum.observed_date = addendum_date.date()
            addendum.created_date = datetime.utcnow()
            addendum.created_by = request.user.username
            for f in formset.forms:
                obsa = CObservation()
                obsa.doc_id = addendum._id
                obsa.pact_id = pact_id
                obsa.provider = request.user.username
                obsa.observed_date = addendum_date
                obsa.anchor_date = addendum_date
                obsa.submited_date = datetime.utcnow()
                obsa.created_date = datetime.utcnow()
                if f.cleaned_data['drug_type'] == 'art':
                    obsa.is_art = True
                elif f.cleaned_data['drug_type'] == 'nonart':
                    obsa.is_art = False
                else:
                    raise Exception("Error, inbound form data invalid")
                obsa.dose_number = f.cleaned_data['dose_number']
                obsa.total_doses = f.cleaned_data['dose_total']
                obsa.adherence = f.cleaned_data['doses_taken']
                obsa.method = f.cleaned_data['observation_type']
                obsa.day_index = -1
                obsa.is_reconciliation = True
                if obsa.is_art:
                    addendum.art_observations.append(obsa)
                else:
                    addendum.nonart_observations.append(obsa)
            addendum.save()
        else:
            raise Exception("error")
    else:
        #it's a GET
        #it's already there, we want to review the reconciliations
        conflicts_dict, is_reconciled = _get_observations_for_date(addendum_date, pact_id, art_num, nonart_num)
        reconciled_doc_id = None

        #first art, then nonart
        data = []
        for n in range(art_num):
            data.append({'drug_type': 'art', 'dose_number': n, 'dose_total': art_num})
        for n in range(nonart_num):
            data.append({'drug_type': 'nonart', 'dose_number': n, 'dose_total': nonart_num})
        formset = AddendumFormSetFactory(initial=data)

        for n in range(art_num):
            form = formset.forms[n]
            if conflicts_dict['ART'].has_key(TIME_LABEL_LOOKUP[art_num][n]):
                form.conflicts = conflicts_dict['ART'][TIME_LABEL_LOOKUP[art_num][n]]
            else:
                form.conflicts = []
            context['art_forms'].append(form)
        for n in range(nonart_num):
            form = formset.forms[n + art_num]
            if conflicts_dict['Non ART'].has_key(TIME_LABEL_LOOKUP[nonart_num][n]):
                form.conflicts = conflicts_dict['Non ART'][TIME_LABEL_LOOKUP[nonart_num][n]]
            else:
                form.conflicts = []
            context['nonart_forms'].append(form)
        context['formset'] = formset
        context['is_reconciled'] = is_reconciled

        if is_reconciled:
            for drug_type, time_labels_dict in conflicts_dict.items():
                for time_label, observations in time_labels_dict.items():
                    for obs in observations:
                        if getattr(obs, 'is_reconciliation', False):
                            reconciled_doc_id = obs.doc_id
                            break
                    if reconciled_doc_id != None:
                        break
                if reconciled_doc_id != None:
                    break
            context['doc_id'] = reconciled_doc_id
    return  render_to_response(template, context_instance=context)


@login_required
def debug_case_dots(request, template='dots/debug_dots.html'):
    context = get_couchdata(request)
    #need to parse context again and do lookups from patient case data
    full_dates = context['full_dates']
    def realdate(d):
        return d[0] != None

    def raw_obs_for_date(date):
        datekey = [patient.couchdoc.pact_id, 'observe_date', date.year, date.month, date.day]
        raw_obs = CObservation.view('pactcarehq/dots_observations', key=datekey).all()
        raw_obs = sorted(raw_obs, key=lambda x: x.anchor_date, reverse=True)
        artmatrix = {}
        nonartmatrix = {}
        for r in raw_obs:
            if r.is_art:
                if not artmatrix.has_key(r.dose_number):
                    artmatrix[r.dose_number] = [] #keyed by dose num
                artmatrix[r.dose_number].append(r)
            else:
                if not nonartmatrix.has_key(r.dose_number):
                    nonartmatrix[r.dose_number] = [] #keyed by dose num
                nonartmatrix[r.dose_number].append(r)
        return { "ART" : artmatrix, "Non-ART": nonartmatrix }

    #(date, calendar_display, casedata, [component_submissions])

    patient = context['patient']
    if patient != None:
        cal_obs = filter(realdate, context['new_dates'])
        art_num = patient.couchdoc.art_num
        non_art_num = patient.couchdoc.non_art_num


        results = [(cal[0], cal[1], patient.couchdoc.dots_casedata_for_day(cal[0], art_num, non_art_num), raw_obs_for_date(cal[0])) for cal in cal_obs]
        context['debug_data'] = results

    return  render_to_response(template, context_instance=context)




@login_required
def index_couch(request, template='dots/index_couch.html'):
    context = get_couchdata(request)
    return  render_to_response(template, context_instance=context)



def get_couchdata(request):
    end_date = _parse_date(request.GET.get('end', datetime.utcnow()))
    start_date = _parse_date(request.GET.get('start', end_date - timedelta(14)))
    patient_id = request.GET.get('patient', None)

    do_pdf = request.GET.get('pdf', False)

    if start_date > end_date:
        end_date = start_date
    elif end_date - start_date > timedelta(365):
        end_date = start_date + timedelta(365)

    try:
        patient = Patient.objects.get(id=patient_id)
        pact_id = patient.couchdoc.pact_id


    except:
        patient = None
        pact_id = None

    view_doc_id = request.GET.get('submit_id', None)

    if view_doc_id != None:
        #we want to see a direct single instance display. override the display times
        observations = CObservation.view('pactcarehq/dots_observations', key=['doc_id', view_doc_id]).all()
    else:
        startkey = [pact_id, 'anchor_date', start_date.year, start_date.month, start_date.day]
        endkey = [pact_id, 'anchor_date', end_date.year, end_date.month, end_date.day]
        observations = CObservation.view('pactcarehq/dots_observations', startkey=startkey, endkey=endkey).all()

    total_doses_set = set([obs.total_doses for obs in observations])
    observed_dates = list(set([s.observed_date for s in observations]))
    sorted_obs = sorted(observations, key=lambda k:k['observed_date'])

    if len(observed_dates) > 0:
        min_date = min(observed_dates)
        max_date = max(observed_dates)
    else:
        min_date = datetime.utcnow()
        max_date = datetime.utcnow()

    full_dates = []
    days_delta = (max_date - min_date).days
    full_dates = [min_date + timedelta(days=x) for x in range(0,days_delta+2)]
    #while date <= max_date:
        #full_dates.append(date)
        #date += timedelta(1)

    if view_doc_id != None:
        visits_set = set([view_doc_id])
    else:
        visits_set = set([obs.doc_id for obs in observations])


    timekeys = set()
    for d in total_doses_set:
        try:
            timekeys = set.union(timekeys, set(CObservation.get_time_labels(d)))
        except:
            pass

#        timekeys = set.union(*map(set, map(CObservation.get_time_labels, total_doses_set)))
#        timekeys = sorted(timekeys, key=TIME_LABELS.index)

    artkeys = ('ART', 'Non ART')
    def group_by_is_art_and_time(date):
        grouping = {}
        conflict_dict = {}
        day_notes = []
        conflict_check = {}
        found_reconcile = False
        for artkey in artkeys:
            by_time = {}
            for timekey in timekeys:
                by_time[timekey] = []
            grouping[artkey] = by_time

        if date:
            datekey = [pact_id, 'observe_date', date.year, date.month, date.day]
            obs = CObservation.view('pactcarehq/dots_observations', key=datekey).all()
            for ob in obs:
                try:
                    time_label = ob.get_time_label()
                except IndexError:
                    logging.error("Error, observation time label index not found, DOT data generation error")
                    time_label = TIME_LABELS[ob.dose_number]

                #if any observation on this date has a notes for that particular check, record it.
                if ob.day_note != None and ob.day_note != '' and day_notes.count(ob.day_note) == 0:
                    day_notes.append(ob.day_note)
                    #pre-check
                if ob.is_reconciliation == True:
                    #it's a reconciled entry.  Trump all
                    grouping['ART' if ob.is_art else 'Non ART'][time_label] = [ob]
                    found_reconcile = True
                    print "found reconciliation: %s" % (ob.doc_id)
                    continue
                else:
                    #base case if it's never been seen before, add it as the key
                    if not conflict_check.has_key(ob.adinfo[0]):
                        conflict_check[ob.adinfo[0]] = ob

                    #main check.  for the given key adinfo[0], check to see if the value is identical
                    prior_ob = conflict_check[ob.adinfo[0]]
                    if prior_ob.adinfo[1] != ob.adinfo[1]:
                        #they don't match, add the current ob to the conflict dictionary
                        if not conflict_dict.has_key(ob.doc_id):
                            conflict_dict[ob.doc_id] = ob
                            #next, add the one existing in the lookup checker as well because they differed.
                        if not conflict_dict.has_key(prior_ob.doc_id):
                            conflict_dict[prior_ob.doc_id] = prior_ob
                    conflict_check[ob.adinfo[0]] = ob

                    if view_doc_id != None and ob.doc_id != view_doc_id:
                        #print "\tSkip:Is ART: %s: %d/%d %s:%s" % (ob.is_art, ob.dose_number, ob.total_doses, ob.adherence, ob.method)
                        #skip if we're only looking at one doc
                        continue
                    else:
                        #show it because we're looking at all observations
                        #print "\tShow:Is ART: %s: %d/%d %s:%s" % (str(ob.is_art)[0], ob.dose_number, ob.total_doses, ob.adherence, ob.method)
                        pass

                    if not found_reconcile and time_label != '':
                        if grouping['ART' if ob.is_art else 'Non ART'].has_key(time_label) == False:
                            grouping['ART' if ob.is_art else 'Non ART'][time_label] = []
                            logging.error("Error, a key not expected was found in this entry: ob doc: %s, day index: %d, art status: %s, dose: %d/%d, is reconciled: %s" % (ob.doc_id, ob.day_index, ob.is_art, ob.dose_number, ob.total_doses, ob.is_reconciliation))

                        grouping['ART' if ob.is_art else 'Non ART'][time_label].append(ob)

        #for each class of drug (art, non art) in artkeys
        #for each time in the timeslots (morning, afternoon, etc)
        #get the most recent observation for that time slot observed_date[-1:] - make it a list because we iterate through them
        if found_reconcile == False:
            #little hacky here, but if we've found reconciliation items, then we can skip showing the conflict list
            conflict_list = sorted(conflict_dict.values(), key=lambda x: x.anchor_date, reverse=True)
        else:
            conflict_list = []

        return (
        [(ak, [(tk, sorted(grouping[ak][tk], key=lambda x: x.anchor_date)[-1:]) for tk in timekeys]) for ak in artkeys],
        conflict_list, day_notes, found_reconcile)

    start_padding = full_dates[0].weekday()
    end_padding = 7 - full_dates[-1].weekday() + 1
    full_dates = [None] * start_padding + full_dates + [None] * end_padding
    #week = [[date, entry]...]
    #entry = [('non_art', [(time1: [obs1, obs2, obs3]), (time2,[obs4, obs5]), (time3,[obs7]),...]), ('art', [(time1:[obs1,obs2...]), (time2, [obs3]), ...])... '
    #time = [ 

    #observed_dates = [(date, group_by_is_art_and_time(date)) for date in observed_dates] #week = [[date, entries],...], where entry = [{art:
    #weeks = [observed_dates[7*n:7*(n+1)] for n in range(len(observed_dates)/7)]
    new_dates = []
    for date in full_dates:
        observation_tuple = group_by_is_art_and_time(date)#entries = 0, conflicts = 1, notes=2, reconcile=3
        new_dates.append((date, observation_tuple[0], observation_tuple[1], observation_tuple[2], observation_tuple[3]))
    weeks = [new_dates[7 * n:7 * (n + 1)] for n in range(len(new_dates) / 7)]

    dots_pts = CPatient.view('patient/all_dots', include_docs=True).all()
    dots_ids = [pt._id for pt in dots_pts]
    patients = Patient.objects.filter(doc_id__in=dots_ids)

    visit_docs = [XFormInstance.view('pactcarehq/all_submits_raw', key=visit_id, include_docs=True).first() for visit_id in visits_set]
    while visit_docs.count(None) > 0:
        visit_docs.remove(None) #this is a bit hacky, some of the visit_ids are actually reconcile doc_ids, so we need to remove the ones that return None from the view

    sorted_visits = sorted(visit_docs, key=lambda d: d.received_on)

    #sanity check if we're running with old data:
    if patients.count() == 0:
        patients = Patient.objects.all()

    patients = sorted(patients, key=lambda p: p.couchdoc.last_name + p.couchdoc.first_name)
    if patient:
        art_regimen = patient.couchdoc.art_regimen
        try:
            art_num = int(ghetto_regimen_map[art_regimen.lower()])
        except:
            art_num = 0

        nonart_regimen = patient.couchdoc.non_art_regimen
        try:
            nonart_num = int(ghetto_regimen_map[nonart_regimen.lower()])
        except:
            nonart_num = 0
    else:
        art_num = 0
        nonart_num = 0

    context = RequestContext(request, locals())
    {
        'weeks': weeks,
        'patients': patients,
        'patient': patient,
        'start_date': start_date,
        'end_date': end_date,
        'min_date': min_date,
        'max_date': max_date,
        'art_num': art_num,
        'nonart_num': nonart_num,
    }

    return context
