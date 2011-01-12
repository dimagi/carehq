from django.db.models.signals import post_init, post_delete
from functools import partial
import simplejson
from patient.models.djangomodels import Patient
from patient.models.couchmodels import CPatient
from django.core.cache import cache

def load_couchpatient_properties(sender, instance, *args, **kwargs):
    for prop in CPatient._properties.keys():
        #this is a bit dirty, but basically in unit tests, the signals don't seem to get actuated for this to set the _couchdoc properties.
        #as a result, doing it on the class level
        setattr(instance, 'cget_%s' % prop, partial(instance._get_COUCHDATA, prop))
        setattr(instance, 'cset_%s' % prop, partial(instance._set_COUCHDATA, prop))
post_init.connect(load_couchpatient_properties, sender=Patient)


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
                instance._couchdoc = CPatient.view('patient/all', key=instance.doc_id, include_docs=True).first()
                couchjson = simplejson.dumps(instance._couchdoc.to_json())
                cache.set('%s_couchdoc' % (instance.id), couchjson)
            except Exception, ex:
                instance._couchdoc = None
        else:
            instance._couchdoc = CPatient.wrap(simplejson.loads(couchjson))
post_init.connect(load_couchpatient, sender=Patient)


def load_couchpatient_properties(sender, instance, *args, **kwargs):
    for prop in CPatient._properties.keys():
        #this is a bit dirty, but basically in unit tests, the signals don't seem to get actuated for this to set the _couchdoc properties.
        #as a result, doing it on the class level
        setattr(instance, 'cget_%s' % prop, partial(instance._get_COUCHDATA, prop))
        setattr(instance, 'cset_%s' % prop, partial(instance._set_COUCHDATA, prop))
post_init.connect(load_couchpatient_properties, sender=Patient)




def patient_post_delete(sender, instance, *args, **kwargs):
    if instance.couchdoc != None:
        doc = instance.couchdoc
        doc.delete()

post_delete.connect(patient_post_delete, sender=Patient )
