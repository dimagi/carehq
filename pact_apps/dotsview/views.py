from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from models import *
from django.contrib.auth.decorators import login_required
from patient.models.couchmodels import CPatient
from couchforms.models import XFormInstance

import csv


def _parse_date(string):
    if isinstance(string, basestring):
        return datetime.datetime.strptime(string, "%Y-%m-%d").date()
    else:
        return string


@login_required
def get_csv(request):
    csv_mode = request.GET.get('csv', None)
    end_date = _parse_date(request.GET.get('end', datetime.date.today()))
    start_date = _parse_date(request.GET.get('start', end_date-datetime.timedelta(30)))
    view_doc_id = request.GET.get('submit_id', None)
    patient_id = request.GET.get('patient', None)
    
    try:
        patient = Patient.objects.get(id=patient_id)        
        pact_id = patient.couchdoc.pact_id
    except:
        patient = None
        pact_id=None
     
    response = HttpResponse(mimetype='text/csv')
    writer = csv.writer(response, dialect=csv.excel)
    if csv_mode == 'all':
        start_date = end_date - datetime.timedelta(1000)
        startkey = [pact_id,  start_date.year, start_date.month, start_date.day]
        endkey = [pact_id,  end_date.year, end_date.month, end_date.day]
        observations = CObservation.view('pactcarehq/dots_observations', startkey=startkey, endkey=endkey).all()
        response['Content-Disposition'] = 'attachment; filename=dots_csv_pt_%s.csv' % (pact_id)
    else:
        startkey = [pact_id,  start_date.year, start_date.month, start_date.day]
        endkey = [pact_id,  end_date.year, end_date.month, end_date.day]
        observations = CObservation.view('pactcarehq/dots_observations', startkey=startkey, endkey=endkey).all()
        response['Content-Disposition'] = 'attachment; filename=dots_csv_pt_%s-%s_to_%s.csv' % (pact_id, start_date.strftime("%Y-%m-%d"),  end_date.strftime("%Y-%m-%d"))
    
   # Create the HttpResponse object with the appropriate CSV header.
   

    for num, obs in enumerate(observations):
        dict_obj = obs.to_json()
        if num == 0:
            writer.writerow(dict_obj.keys())
        writer.writerow([dict_obj[x] for x in dict_obj.keys()])

    return response

#@login_and_domain_required
@login_required
def index(request, template='dots/index.html'):
    end_date = _parse_date(request.GET.get('end', datetime.date.today()))
    start_date = _parse_date(request.GET.get('start', end_date-datetime.timedelta(14)))
    patient_id = request.GET.get('patient', None)
    
    if start_date > end_date:
         end_date = start_date
    elif end_date - start_date > datetime.timedelta(365):
         end_date = start_date + datetime.timedelta(365) 
    dates = []
    date = start_date
    while date <= end_date:
        dates.append(date)
        date += datetime.timedelta(1)

    try:
        patient = Patient.objects.get(id=patient_id)
    except:
        patient = None

    observations = Observation.objects.filter(patient__id=patient_id)
    if observations.count():
        agg = observations.aggregate(Max('date'), Min('date'))
        first_observation = agg['date__min']
        last_observation = agg['date__max']
        del agg
        if end_date < first_observation or last_observation < start_date:
            bad_date_range = True
    total_doses_set = set(observations.values_list('total_doses', flat=True))

    try:
        timekeys = set.union(*map(set, map(Observation.get_time_labels, total_doses_set)))
        timekeys = sorted(timekeys, key=TIME_LABELS.index)
    except:
        timekeys = []

    artkeys = ('ART', 'Non ART')
    
    def group_by_is_art_and_time(date):
        grouping = {}
        for artkey in artkeys:
            by_time = {}
            for timekey in timekeys:
                by_time[timekey] = []
            grouping[artkey] = by_time
        obs = observations.filter(date=date)
        for ob in obs:
            grouping['ART' if ob.is_art else 'Non ART'][ob.get_time_label()].append(ob)
        
        return [(ak, [(tk, sorted(grouping[ak][tk], key=lambda x: x.date)[-1:]) for tk in timekeys]) for ak in artkeys]
    
    start_padding = dates[0].weekday()
    end_padding = 7-dates[-1].weekday() + 1
    dates = [None]*start_padding + dates + [None]*end_padding

    dates = [(date, group_by_is_art_and_time(date)) for date in dates]
    weeks = [dates[7*n:7*(n+1)] for n in range(len(dates)/7)]
    
#    patients = Patient.objects.filter(observation__in=Observation.objects.all()).distinct()
    dots_pts = CPatient.view('patient/all_dots', include_docs=True).all()
    dots_ids = []
    for dotpt in dots_pts:
        dots_ids.append(dotpt._id)
    patients = Patient.objects.filter(doc_id__in=dots_ids)

    #sanity check if we're running with old data:
    if patients.count() == 0:
        #print "*** no patients"
        patients = Patient.objects.all()
    else:
        #print "** found patients!"
        pass
    
    context = RequestContext(request, locals())
    {
        'weeks' : weeks,
        'patients' : patients,
        'patient' : patient,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render_to_response(template, context)

@login_required
def index_couch(request, template='dots/index_couch.html'):
    end_date = _parse_date(request.GET.get('end', datetime.date.today()))
    start_date = _parse_date(request.GET.get('start', end_date-datetime.timedelta(14)))
    patient_id = request.GET.get('patient', None)
    
    
    view_doc_id = request.GET.get('submit_id', None)
    
    if view_doc_id != None:
        #we want to see a direct single instance display. override the display times
        submit_obs = CObservation.view('pactcarehq/dots_obs_submit', key=view_doc_id).all()
        sorted_obs = sorted(submit_obs, key=lambda k:k['observed_date'])
        dates = set([s.observed_date for s in submit_obs])
        start_date = min(dates)
        end_date = max(dates)
        


    if start_date > end_date:
        end_date = start_date
    elif end_date - start_date > datetime.timedelta(365):
        end_date = start_date + datetime.timedelta(365) 
    dates = []
    date = start_date
    while date <= end_date:
        dates.append(date)
        date += datetime.timedelta(1)

    try:
        patient = Patient.objects.get(id=patient_id)        
        pact_id = patient.couchdoc.pact_id
    except:
        patient = None
        pact_id=None
        

    startkey = [pact_id,  start_date.year, start_date.month, start_date.day]
    endkey = [pact_id,  end_date.year, end_date.month, end_date.day]
    observations = CObservation.view('pactcarehq/dots_observations', startkey=startkey, endkey=endkey).all()
    total_doses_set = set([obs.total_doses for obs in observations])
    
    
    if view_doc_id != None:
        visits_set = set([view_doc_id])
    else:
        visits_set = set([obs.doc_id for obs in observations])
        #for v in visits_set:
            #print v

    try:
        timekeys = set.union(*map(set, map(CObservation.get_time_labels, total_doses_set)))
        timekeys = sorted(timekeys, key=TIME_LABELS.index)
    except:
        timekeys = []

    artkeys = ('ART', 'Non ART')
    
    def group_by_is_art_and_time(date):
        grouping = {}
        conflict_dict = {}
        day_notes = []
        conflict_check={}
        for artkey in artkeys:
            by_time = {}
            for timekey in timekeys:
                by_time[timekey] = []
            grouping[artkey] = by_time
            
        
            
        if date:
            datekey = [pact_id, date.year, date.month, date.day]
            obs = CObservation.view('pactcarehq/dots_observations', key=datekey).all()
            for ob in obs:
                #base case if it's never been seen before, add it as the key
                if not conflict_check.has_key(ob.adinfo[0]):
                    conflict_check[ob.adinfo[0]]= ob
                    
                #main check.  for the given key adinfo[0], check to see if the value is identical
                prior_ob = conflict_check[ob.adinfo[0]]
                if prior_ob.adinfo[1] != ob.adinfo[1]:
                    #they don't match, add the current ob to the conflict dictionary
                    if not conflict_dict.has_key(ob.doc_id):
                        conflict_dict[ob.doc_id] = ob
                        
                    #next, add the one existing in the lookup checker as well because they differed.
                    if not conflict_dict.has_key(prior_ob.doc_id):
                        conflict_dict[prior_ob.doc_id] = prior_ob
                #if any observation on this date has a notes for that particular check, record it.
                if ob.day_note != None and ob.day_note != '' and day_notes.count(ob.day_note) == 0:
#                    print "\n\nSaving a note"
#                    print ob.doc_id
#                    print date
#                    print ob.adinfo[0]
#                    print ob.adinfo[1]
#                    print ob.day_note
                    day_notes.append(ob.day_note)

                conflict_check[ob.adinfo[0]]= ob
                
                if view_doc_id != None and ob.doc_id != view_doc_id:
                    #print "\tSkip:Is ART: %s: %d/%d %s:%s" % (ob.is_art, ob.dose_number, ob.total_doses, ob.adherence, ob.method)
                    continue
                else:
                    #print "\tShow:Is ART: %s: %d/%d %s:%s" % (str(ob.is_art)[0], ob.dose_number, ob.total_doses, ob.adherence, ob.method)
                    pass
                grouping['ART' if ob.is_art else 'Non ART'][ob.get_time_label()].append(ob)

        #for each class of drug (art, non art) in artkeys
        #for each time in the timeslots (morning, afternoon, etc)
        #get the most recent observation for that time slot observed_date[-1:] - make it a list because we iterate through them

        return ([(ak, [(tk, sorted(grouping[ak][tk], key=lambda x: x.observed_date)[-1:]) for tk in timekeys]) for ak in artkeys], conflict_dict.values(), day_notes)

    
    start_padding = dates[0].weekday()
    end_padding = 7-dates[-1].weekday() + 1
    dates = [None]*start_padding + dates + [None]*end_padding
    #week = [[date, entry]...]
    #entry = [('non_art', [(time1: [obs1, obs2, obs3]), (time2,[obs4, obs5]), (time3,[obs7]),...]), ('art', [(time1:[obs1,obs2...]), (time2, [obs3]), ...])... '
    #time = [ 

    #dates = [(date, group_by_is_art_and_time(date)) for date in dates] #week = [[date, entries],...], where entry = [{art:
    #weeks = [dates[7*n:7*(n+1)] for n in range(len(dates)/7)]
    
    
    
    new_dates = [] 
    for date in dates:
        observation_tuple = group_by_is_art_and_time(date)#entries = 0, conflicts = 1
        new_dates.append((date, observation_tuple[0], observation_tuple[1], observation_tuple[2]))
    weeks = [new_dates[7*n:7*(n+1)] for n in range(len(new_dates)/7)]
    
    dots_pts = CPatient.view('patient/all_dots', include_docs=True).all()
    dots_ids = [pt._id for pt in dots_pts]
    patients = Patient.objects.filter(doc_id__in=dots_ids)
    
    visit_docs = [XFormInstance.view('pactcarehq/all_submits_raw', key=visit_id, include_docs=True).first() for visit_id in visits_set]
    sorted_visits = sorted(visit_docs, key=lambda d: d.received_on)
    
    #sanity check if we're running with old data:
    if patients.count() == 0:
        print "*** no patients"
        patients = Patient.objects.all()
    else:
        print "** found patients!"
    
    patients = sorted(patients, key=lambda p: p.couchdoc.last_name+p.couchdoc.first_name)
    
    context = RequestContext(request, locals())
    {
        'weeks' : weeks,
        'patients' : patients,
        'patient' : patient,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render_to_response(template, context)