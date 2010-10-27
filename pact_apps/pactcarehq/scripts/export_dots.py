from dotsview.models import Observation
from patient.models.djangomodels import Patient

def run():
    observations = Observation.objects.all()
    fields = ['observation_id', 'pt_pact_id', 'date','is_art', 'adherence','method','note','dose_number','total_doses']
    print ','.join(fields)
    for obs in observations:
        output = []
        output.append(str(obs.id))
        output.append(obs.patient.couchdoc['pact_id'])
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

        #print output
        print ','.join(output)





