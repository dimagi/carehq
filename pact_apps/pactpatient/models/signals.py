from django.db.models.signals import post_init
from pactpatient.models.pactmodels import PactPatient
from patient.models import Patient
from functools import partial

def load_couchpatient_properties(sender, instance, *args, **kwargs):
    for prop in PactPatient._properties.keys():
        #this is a bit dirty, but basically in unit tests, the signals don't seem to get actuated for this to set the _couchdoc properties.
        #as a result, doing it on the class level
        setattr(instance, 'cget_%s' % prop, partial(instance._get_COUCHDATA, prop))
        setattr(instance, 'cset_%s' % prop, partial(instance._set_COUCHDATA, prop))
post_init.connect(load_couchpatient_properties, sender=Patient)
