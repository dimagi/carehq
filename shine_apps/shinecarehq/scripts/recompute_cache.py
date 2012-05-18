from patient.models import Patient
from shinepatient.models import ShinePatient

def run():
    """Help script to regenerate a django patient model when couch has replicated the patient docs"""
    pdocs = ShinePatient.view('shinepatient/shine_patients', include_docs=True).all()
    updated = False
    for pdoc in pdocs:
        try:
            pdoc.compute_cache()
        except Exception, ex:
            print "Error trying to compute cache: %s: %s" % (pdoc._id, ex)
    if not updated:
        print "All couch patients are in sync with django!!"

