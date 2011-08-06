import uuid
from couchdbkit.ext.django.schema import Document
from dimagi.utils.couch.database import get_db
from pactpatient.models.pactmodels import PactPatient
from patient.models import Patient
import time
db = get_db()
def run():
    """Script to flip CPatient to PactPatient (subclass of BasePatient), then switch doc_id to a new id, and assign a case_id fromt he original doc_id
    """


    print "This migration has already been completed in production"
    return

    #django patient -> django_uuid = new
    #cpatient-> doc_id = case_id, doc_id = new, == to djpatient.django_uuid

    #this needs to be coupled with fixing up the patient/all querying
    #patient/all needs to emit the case_id
    patients = Patient.objects.all()
    db = get_db()
    for p in patients:
        print "Flipping ID Patient ID: %s: Couchdoc: %s" % (p.id, p.doc_id)
        #so the p.couchdoc is useless here because if the model code is changed we need to do it manually.

        #establish the updated ids and get them separated out
        real_case_id = p.doc_id + "" #the doc_id had been used as the case_id which in real casexml, that's bad.
        new_doc_id = uuid.uuid4().hex #now make a new doc_id for the patient document.

        couchdoc = db.open_doc(p.doc_id)

        #flip the document ids.
        copy_doc = PactPatient.wrap(couchdoc)
        copy_doc.case_id = real_case_id
        copy_doc._id = new_doc_id
        copy_doc.doc_type = PactPatient.__name__
        copy_doc.save()
        p.doc_id = new_doc_id
        p._couchdoc = copy_doc
        p.save()
        print "\tSwapping case id %s -> %s" % (real_case_id, new_doc_id)

        #having just saved it, we need to now remove the original id
        dupe_doc = db.open_doc(real_case_id) #the old doc_id
        delresult = db.delete_doc(dupe_doc)
        print "\tDeleting doc %s" % (real_case_id)
        print "\t%s" % (delresult)

        i = 0
        while db.doc_exist(real_case_id):
            i+= 1
            print "\tTrying to freaking delete!!!"
            print "\tReally deleting doc %s" % (real_case_id)
            delresult = db.delete_doc(dupe_doc)
            print "\t%s" % (delresult)
            if i == 10:
                break




