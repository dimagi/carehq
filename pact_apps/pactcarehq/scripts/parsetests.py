from clinical_core.patient.models import Patient
from couchforms.models import XFormInstance
from casexml.apps.case.models import CommCareCase

import simplejson
import ujson
import json
import anyjson
from django.utils import simplejson as djangojson

from datetime import datetime
from clinical_shared.utils import ms_from_timedelta


RUNS = 20


def run():
    patients = Patient.objects.all()
    #xforms = XFormInstance.view('couchforms/by_xmlns', key='http://dev.commcarehq.org/pact/progress_note', reduce=False, include_docs=True, limit=6000).all()
    xforms = XFormInstance.view('couchforms/by_xmlns', key='http://code.javarosa.org/devicereport', reduce=False, include_docs=True, limit=6000).all()

    patient_json = [x.couchdoc.to_json() for x in patients]
    case_json = [CommCareCase.get_db().get(x.couchdoc.case_id) for x in patients]
    xforms_json = [x.to_json() for x in xforms]


    print "Total items: %d patients, %d cases, %d xforms" % (len(patient_json), len(case_json), len(xforms_json))

    modules = [simplejson, ujson, json, djangojson, anyjson]
    sources = [patient_json, case_json, xforms_json, [patient_json, case_json, xforms_json], [[patient_json, case_json, xforms_json]] ]

    results = {}

    for mod in modules:
        encoded = []
        encode_start = datetime.utcnow()
        for arr in sources:
            source_encoded = []
            for item in arr:
                source_encoded.append(mod.dumps(item))
            encoded.append(source_encoded)
        encode_end = datetime.utcnow()
        encode_time = ms_from_timedelta(encode_end - encode_start)

        decode_start = datetime.utcnow()
        for arr in encoded:
            for item in arr:
                mod.loads(item)
        decode_end = datetime.utcnow()
        decode_time = ms_from_timedelta(decode_end - decode_start)
        results[mod] = (encode_time, decode_time)


    print "Results:"
    for k, v in results.items():
        print "%s" % k
        print "\tdumps: %.2f seconds" % ( v[0]/1000.)
        print "\tloads: %.2f seconds" % ( v[1]/1000.)



