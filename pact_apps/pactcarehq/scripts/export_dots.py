from dotsview.models import Observation
from patient.models.djangomodels import Patient
from couchforms.models import XFormInstance
from datetime import datetime

def run():
    observations = Observation.objects.all()
    fields = ['observation_id', 'observation_date', 'pt_pact_id', 'check_date','is_art', 'adherence','method','note','dose_number','total_doses', 'anchor_date']
    print ','.join(fields)
    for obs in observations:
        output = []
        output.append(str(obs.doc_id))
        doc = XFormInstance.view('pactcarehq/all_submits_raw', key=obs.doc_id).first()
        if (doc):
            output.append(doc['form']['encounter_date'].strftime('%Y-%m-%d'))
        else:
            output.append("no-encounter")
            print "WTF"

        output.append(obs.patient.couchdoc()['pact_id'])
        output.append(obs.date.strftime("%Y-%m-%d"))
        if obs.is_art:
            output.append('1')
        else:
            output.append('0')
        output.append(obs.adherence)
        output.append(obs.method)
        if obs.note:
            output.append(obs.note)
        else:
            output.append('')
        output.append(repr(obs.dose_number))
        output.append(repr(obs.total_doses))

        if doc:
            anchor = doc['form']['case']['update']['dots']['anchor']
            anchor_date = datetime.strptime(anchor, "%d %b %Y %H:%M:%S %Z")
            output.append(anchor_date.strftime('%Y-%m-%d'))
        else:
            output.append("no-anchor")

        #print output
        print ','.join(output)





