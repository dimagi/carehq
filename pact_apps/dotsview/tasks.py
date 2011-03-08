#on demand task to queue up csv generation and send out email to admin
import csv
from datetime import datetime
from celery.decorators import task
from django.http import HttpResponse
from dimagi.utils.couch.database import get_db
from dotsview.models.couchmodels import CObservation
from dotsview.views import _parse_date
from patient.models.djangomodels import Patient

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO


@task
def csv_export(request):
    csv_mode = request.GET.get('csv', None)
    end_date = _parse_date(request.GET.get('end', datetime.date.today()))
    start_date = _parse_date(request.GET.get('start', end_date - datetime.timedelta(30)))
    view_doc_id = request.GET.get('submit_id', None)
    patient_id = request.GET.get('patient', None)

    try:
        patient = Patient.objects.get(id=patient_id)
        pact_id = patient.couchdoc.pact_id
    except:
        patient = None
        pact_id = None

    container = StringIO() #HttpResponse(mimetype='text/csv')
    writer = csv.writer(container, dialect=csv.excel)
    if patient != None:
        if csv_mode == 'all':
            start_date = end_date - datetime.timedelta(1000)
            startkey = [pact_id.encode('ascii'), 'anchor_date', start_date.year, start_date.month, start_date.day]
            endkey = [pact_id.encode('ascii'), 'anchor_date', end_date.year, end_date.month, end_date.day]
            observations = CObservation.view('pactcarehq/dots_observations', startkey=startkey, endkey=endkey).all()
            container['Content-Disposition'] = 'attachment; filename=dots_csv_pt_%s.csv' % (pact_id)
        else:
            startkey = [pact_id.encode('ascii'), 'anchor_date', start_date.year, start_date.month, start_date.day]
            endkey = [pact_id.encode('ascii'), 'anchor_date', end_date.year, end_date.month, end_date.day]
            observations = CObservation.view('pactcarehq/dots_observations', startkey=startkey, endkey=endkey).all()
            container['Content-Disposition'] = 'attachment; filename=dots_csv_pt_%s-%s_to_%s.csv' % (
            pact_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    elif patient == None:
        if csv_mode == 'all':
            start_date = end_date - datetime.timedelta(1000)
            startkey = [start_date.year, start_date.month, start_date.day]
            endkey = [end_date.year, end_date.month, end_date.day]
            observations = CObservation.view('pactcarehq/dots_observations', startkey=startkey, endkey=endkey).all()
            container['Content-Disposition'] = 'attachment; filename=dots_csv_pt_all.csv'
        else:
            startkey = [start_date.year, start_date.month, start_date.day]
            endkey = [end_date.year, end_date.month, end_date.day]
            observations = CObservation.view('pactcarehq/dots_observations', startkey=startkey, endkey=endkey).all()
            container['Content-Disposition'] = 'attachment; filename=dots_csv_pt_all-%s_to_%s.csv' % (
            start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
            # Create the HttpResponse object with the appropriate CSV header.

    db = get_db()

    csv_keys = ['submitted_date', u'note', u'patient', 'doc_type', 'is_reconciliation', u'provider', u'day_index', 'day_note', u'encounter_date', u'anchor_date', u'total_doses', u'pact_id', u'dose_number', u'created_date', u'is_art', u'adherence', '_id', u'doc_id', u'method', u'observed_date']
    for num, obs in enumerate(observations):
        dict_obj = obs.to_json()
        if num == 0:
            writer.writerow(csv_keys)
        writer.writerow([dict_obj[x] for x in csv_keys])

    return container
