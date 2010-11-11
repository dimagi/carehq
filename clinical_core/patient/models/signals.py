from django.db.models.signals import post_init, post_delete
from functools import partial
from patient.models.djangomodels import Patient

def load_couchpatient(sender, instance, *args, **kwargs):
    if instance.couchdoc != None:
        for prop in instance.couchdoc._properties.keys():
            setattr(instance, 'cget_%s' % prop, partial(instance._get_COUCHDATA, prop))
            setattr(instance, 'cset_%s' % prop, partial(instance._set_COUCHDATA, prop))

post_init.connect(load_couchpatient, sender=Patient)



def patient_post_delete(sender, instance, *args, **kwargs):
    if instance.couchdoc != None:
        doc = instance.couchdoc
        doc.delete()
    pass

post_delete.connect(patient_post_delete, sender=Patient )
