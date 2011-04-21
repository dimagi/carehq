import uuid
from dimagi.utils.couch.database import get_db
from patient.models.djangomodels import Patient

def run():
    """Need to fix CPatient and djangopatient to use id's DIFFERENT from case_id"""

    #django patient -> django_uuid = new
    #cpatient-> doc_id = case_id, doc_id = new, == to djpatient.django_uuid

    #this needs to be coupled with fixing up the patient/all querying
    #patient/all needs to emit the case_id
    patients = Patient.objects.all()
    for p in patients:
        print "Patient %s, %s" % (p.id, p.doc_id)
        if p.couchdoc == None:
            print "\tSkipped!"
            continue
        couchdoc = p.couchdoc
        real_case_id = p.doc_id
        new_doc_id = uuid.uuid1().hex

        #flip the document ids.
        couchdoc._id = new_doc_id
        couchdoc.case_id = real_case_id
        p.doc_id = new_doc_id
        couchdoc.save()
        p.save()

        #having just saved it, we need to now remove the original id
        db = get_db()
        dupe_doc = db.open_doc(real_case_id) #the old doc_id
        db.delete_doc(dupe_doc)



