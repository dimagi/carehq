from couchdbkit.exceptions import ResourceNotFound
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import   post_init, post_delete
import logging
from actorpermission.models import BaseActorDocument, PatientActor, ProviderActor, CaregiverActor
from permissions.models import Actor
import settings

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
    Cleanup procedure to ensure that a deleted actor is deprecated and removed from the view.
    """
    if not instance.doc_id:
        logging.debug("Document doesn't exist")
        return
    if not hasattr(instance, 'actordoc'):
        doc = BaseActorDocument.get_typed_from_id(instance.doc_id)
    else:
        doc = instance.actordoc
    if doc is not None:
        if doc != None:
            #delete manually
            doc._deprecate_data()
    else:
        logging.debug("Document already removed")
post_delete.connect(actor_post_delete, sender=Actor)


def login_session_check(sender, request, user, **kwargs):
    if request.POST.get('remember_me', None):
        request.session.set_expiry(settings.KEEP_LOGGED_DURATION)
user_logged_in.connect(login_session_check)