from django.db.models.signals import post_init, post_delete
from functools import partial
import simplejson
import logging
from models import BasePatient
from models import Patient
from django.core.cache import cache

def patient_post_delete(sender, instance, *args, **kwargs):
    """
    Cleanup procedure to ensure that a deleted django patient model deprecates/removes the corresponding couchinstance.
    This will fail silently in the corner case where a couchdoc's underlying ID is changed due to a major transform operation.
    """
    if instance.couchdoc != None:
        doc = instance.couchdoc
        #delete manually
        doc._deprecate_data()
    else:
        logging.debug("Document already removed")

post_delete.connect(patient_post_delete, sender=Patient )
