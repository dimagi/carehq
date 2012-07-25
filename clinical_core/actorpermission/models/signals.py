from django.db.models.signals import  post_delete
import logging
from actorpermission.models.actortypes import BaseActorDocument
from permissions.models import Actor
from couchdbkit.exceptions import ResourceNotFound
from django.db.models.signals import   post_init
from actorpermission.models import  PatientActor, ProviderActor, CaregiverActor

def get_actor_doc(sender, instance, *args, **kwargs):
    doc_id=instance.doc_id
    if doc_id is not None:
        #doc = BaseActorDocument.view('actorpermission/all_actors',key=doc_id, include_docs=True).first()
        try:
            doc = BaseActorDocument.get_typed_from_id(doc_id)
            if doc != None:
                instance.actordoc = doc
        except ResourceNotFound:
            pass
post_init.connect(get_actor_doc, sender=Actor)


def set_actor_props(sender, instance, *args, **kwargs):
    """
    Set properties on the django actor based upon the roles of the actor
    """
    if hasattr(instance, 'actordoc'):
        if isinstance(instance.actordoc, PatientActor):
            setattr(instance, 'is_patient', True)
        else:
            setattr(instance, 'is_patient', False)

        if isinstance(instance.actordoc, ProviderActor):
            setattr(instance, 'is_provider', True)
        else:
            setattr(instance, 'is_provider', False)

        if isinstance(instance.actordoc, CaregiverActor):
            setattr(instance, 'is_caregiver',True)
        else:
            setattr(instance, 'is_caregiver', False)
post_init.connect(set_actor_props, sender=Actor)


def actor_post_delete(sender, instance, *args, **kwargs):
    """
    Cleanup procedure to ensure that a deleted django patient model deprecates/removes the corresponding couchinstance.
    This will fail silently in the corner case where a couchdoc's underlying ID is changed due to a major transform operation.
    """

    if instance.doc_id is not None:
        doc_id = instance.doc_id
        try:
            BaseActorDocument.get_db().delete(doc_id)
        except:
            logging.error("unable to delete document")
    else:
        logging.debug("Document already removed")

post_delete.connect(actor_post_delete, sender=Actor)



