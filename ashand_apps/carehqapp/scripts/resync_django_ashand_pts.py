from patient.models import Patient
from shinepatient.models import ShinePatient

def run():
    """Help script to regenerate a django patient model when couch has replicated the patient docs"""
    #first remove dangling django patients.
    django_patients = Patient.objects.all()
    for dj in django_patients:
        if ShinePatient.get_db().doc_exist(dj.doc_id):
            print "patient doc id exists, skipping: %s" % dj.id
            continue
        else:
            print "patient dangling, deleting"
            dj.doc_id = None
            dj.delete()

    print "purged django dangling"

    pdocs = ShinePatient.view('patient/all', include_docs=True).all()
    updated = False
    for pdoc in pdocs:
        try:
            pt = Patient.objects.get(doc_id=pdoc._id)
            if pt.id != pdoc.django_uuid:
                print "\tProblem, django uuids don't match.  Deleting and recreating"
                pt.doc_id = None
                pt.delete()

                print "\t%s %s" % (pdoc.django_uuid, pdoc._id)
                newpt = Patient()
                newpt.save(django_uuid=pdoc.django_uuid, doc_id=pdoc._id)
                print "\tCreated new patient django moddel"
        except Patient.DoesNotExist:
            pt = Patient(id=pdoc.django_uuid, doc_id=pdoc._id)
            pt.save()
            updated=True
            print "creating patient from couchdoc %s:%s" % (pt.id, pt.doc_id)
    if not updated:
        print "All couch patients are in sync with django!!"

