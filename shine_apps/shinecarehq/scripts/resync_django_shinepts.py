from patient.models import Patient
from shinepatient.models import ShinePatient

def run():
    """Help script to regenerate a django patient model when couch has replicated the patient docs"""
    pdocs = ShinePatient.view('shinepatient/shine_patients', include_docs=True).all()
    updated = False
    for pdoc in pdocs:
        try:
            pt = Patient.objects.get(doc_id=pdoc._id)
        except Patient.DoesNotExist:
            pt = Patient(id=pdoc.django_uuid, doc_id=pdoc._id)
            pt.save()
            updated=True
            print "creating patient from couchdoc %s:%s" % (pt.id, pt.doc_id)
    if not updated:
        print "All couch patients are in sync with django!!"

