from django.db.models.signals import   post_init, post_delete
import logging
from actorpermission.models.actortypes import BaseActorDocument
from permissions.models import Actor

def get_actor_doc(sender, instance, *args, **kwargs):
    doc_id=instance.doc_id
    if doc_id is not None:
        #doc = BaseActorDocument.view('actorpermission/all_actors',key=doc_id, include_docs=True).first()
        doc = BaseActorDocument.get_typed_from_id(doc_id)
        if doc != None:
            instance.actordoc = doc
post_init.connect(get_actor_doc, sender=Actor)



def actor_post_delete(sender, instance, *args, **kwargs):
    """
    Cleanup procedure to ensure that a deleted actor is deprecated and removed from the view.
    """
    if hasattr(instance, 'actordoc'):
        doc = instance.actordoc
        if doc != None:
            #delete manually
            doc._deprecate_data()
    else:
        logging.debug("Document already removed")
post_delete.connect(actor_post_delete, sender=Actor)
