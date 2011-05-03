from django.db.models.signals import post_init, post_delete
from functools import partial
import simplejson
from .patientmodels import BasePatient
from .patientmodels import Patient
from django.core.cache import cache



def load_couchpatient(sender, instance, *args, **kwargs):
    """
    Post init signal of a django patient object - pull the corresponding couchdoc instance from couch and/or from memory
    """
    #first, do a memcached lookup
    #print "doing signal to lookup couchdb doc %s: %s" % (instance.id, instance.doc_id)

    if instance.doc_id != None:
        couchjson = cache.get('%s_couchdoc' % (instance.id), None)
        if couchjson == None:
            #memcached lookup got nothing, query again
            try:
                instance._couchdoc = BasePatient.view('patient/all', key=instance.doc_id, include_docs=True).first()
                couchjson = simplejson.dumps(instance._couchdoc.to_json())
                cache.set('%s_couchdoc' % (instance.id), couchjson)
            except Exception, ex:
                instance._couchdoc = None
        else:
            instance._couchdoc = BasePatient.wrap(simplejson.loads(couchjson))
post_init.connect(load_couchpatient, sender=Patient)

def patient_post_delete(sender, instance, *args, **kwargs):
    if instance.couchdoc != None:
        doc = instance.couchdoc
        #delete manually
        doc.doc_type = "Deleted%s" % (doc._get_my_type())
        doc.base_type = "DeletedBasePatient"
        doc.save()

post_delete.connect(patient_post_delete, sender=Patient )
