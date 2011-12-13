from django.contrib.contenttypes.models import ContentType
from actorpermission.models.actortypes import ProviderActor
from pactconfig import constants
import permissions
from permissions.models import Role, PrincipalRoleRelation
from tenant.models import Tenant


def get_external_providers():
    """
    Returns actor documents of external providers in the system
    """
    provider_role = Role.objects.get(name=constants.role_external_provider)
    django_provider_actors = PrincipalRoleRelation.objects.filter(role=provider_role).filter(content_id=None)
    actor_doc_ids = django_provider_actors.distinct().values_list('actor__doc_id', flat=True)
    actor_docs = ProviderActor.view('actorpermission/all_actors', keys=list(actor_doc_ids), include_docs=True).all()
    return actor_docs


def add_external_provider(patient, actor):
    """
    Add an actor as an exteranl provider for the given patient.
    """
    pact_tenant = Tenant.objects.get(name="PACT")
    role_class = Role.objects.get(name=constants.role_external_provider)
    permissions.utils.add_role(provider_actor.django_actor, role_class)
    permissions.utils.add_local_role(patient.django_patient, actor.django_actor, role_class)


def get_permissions(actor_doc):
    djactor = actor_doc.django_actor
    direct_permissions = PrincipalRoleRelation.objects.filter(actor=djactor).exclude(content_id=None)


def get_careteam(patient):
    #django patient
    direct_permissions = PrincipalRoleRelation.objects.filter(content_type=ContentType.objects.get_for_model(patient), content_id=patient.id)
    return direct_permissions

