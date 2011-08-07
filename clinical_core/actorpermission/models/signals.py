from django.db.models.signals import  post_delete
import logging
from actorpermission.models.actortypes import BaseActorDocument
from permissions.models import Actor

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
