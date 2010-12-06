from django.db.models.signals import post_init, post_delete
from functools import partial
from patient.models.djangomodels import Patient
from patient.models.couchmodels import CPatient

def load_couchpatient(sender, instance, *args, **kwargs):
    for prop in CPatient._properties.keys():
        #this is a bit dirty, but basically in unit tests, the signals don't seem to get actuated for this to set the _couchdoc properties.
        #as a result, doing it on the class level
        setattr(instance, 'cget_%s' % prop, partial(instance._get_COUCHDATA, prop))
        setattr(instance, 'cset_%s' % prop, partial(instance._set_COUCHDATA, prop))
post_init.connect(load_couchpatient, sender=Patient)



def patient_post_delete(sender, instance, *args, **kwargs):
    if instance.couchdoc != None:
        doc = instance.couchdoc
        doc.delete()

post_delete.connect(patient_post_delete, sender=Patient )
