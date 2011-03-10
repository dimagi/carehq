#on demand task to queue up csv generation and send out email to admin
import csv
from datetime import datetime, timedelta
import uuid
from celery.decorators import task
from django.http import HttpResponse
import simplejson
from dimagi.utils.couch.database import get_db
from dotsview.models.couchmodels import CObservation
from django.core.cache import cache
from patient.models.djangomodels import Patient
import tempfile, os, zipfile

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO


@task
def csv_export(csv_mode, end_date_str, start_date_str, patient_id, download_id):
    from dotsview.views import _parse_date
    end_date = _parse_date(end_date_str)
    start_date = _parse_date(start_date_str)

    try:
        patient = Patient.objects.get(id=patient_id)
        pact_id = patient.couchdoc.pact_id
    except:
        patient = None
        pact_id = None

    cache_container = {}
    cache_container['mimetype'] = 'application/zip'
    temp_csv = tempfile.TemporaryFile()
    csv_writer = csv.writer(temp_csv, dialect=csv.excel)
    if patient != None:
        if csv_mode == 'all':
            start_date = end_date - timedelta(1000)
            startkey = [pact_id.encode('ascii'), 'anchor_date', start_date.year, start_date.month, start_date.day]
            endkey = [pact_id.encode('ascii'), 'anchor_date', end_date.year, end_date.month, end_date.day]
            observations = CObservation.view('pactcarehq/dots_observations', startkey=startkey, endkey=endkey).all()
            csv_filename = 'dots_csv_pt_%s.csv' % (pact_id)
        else:
            startkey = [pact_id.encode('ascii'), 'anchor_date', start_date.year, start_date.month, start_date.day]
            endkey = [pact_id.encode('ascii'), 'anchor_date', end_date.year, end_date.month, end_date.day]
            observations = CObservation.view('pactcarehq/dots_observations', startkey=startkey, endkey=endkey).all()
            csv_filename = 'dots_csv_pt_%s-%s_to_%s.csv' % (pact_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    elif patient == None:
        if csv_mode == 'all':
            start_date = end_date - timedelta(1000)
            startkey = [start_date.year, start_date.month, start_date.day]
            endkey = [end_date.year, end_date.month, end_date.day]
            observations = CObservation.view('pactcarehq/dots_observations', startkey=startkey, endkey=endkey).all()
            csv_filename = 'dots_csv_pt_all.csv'
        else:
            startkey = [start_date.year, start_date.month, start_date.day]
            endkey = [end_date.year, end_date.month, end_date.day]
            observations = CObservation.view('pactcarehq/dots_observations', startkey=startkey, endkey=endkey).all()
            csv_filename = 'dots_csv_pt_all-%s_to_%s.csv' % (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    csv_keys = ['submitted_date', u'note', u'patient', 'doc_type', 'is_reconciliation', u'provider', u'day_index', 'day_note', u'encounter_date', u'anchor_date', u'total_doses', u'pact_id', u'dose_number', u'created_date', u'is_art', u'adherence', '_id', u'doc_id', u'method', u'observed_date']
    for num, obs in enumerate(observations):
        dict_obj = obs.to_json()
        if num == 0:
            csv_writer.writerow(csv_keys)
        csv_writer.writerow([dict_obj[x] for x in csv_keys])
    temp_csv.seek(0)
    temp_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)

    cache_container['location'] = temp_zip.name
    cache_container['Content-Disposition'] = 'attachment; filename=%s.zip' % (csv_filename)

    zip_file = zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED)
    zip_file.writestr(csv_filename, temp_csv.read())
    temp_csv.close()

    zip_file.close()
    temp_zip.close()
    cache.set(download_id, simplejson.dumps(cache_container), 86400)

