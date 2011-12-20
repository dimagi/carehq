from django.contrib.contenttypes.models import ContentType
from actorpermission.models.actortypes import ProviderActor, CHWActor
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


def add_chw(chw_actor):
    """
    For a given django actor, give it a global role of CHW.
    """
    role_class = Role.objects.get(name=constants.role_chw)
    permissions.utils.add_role(chw_actor.django_actor, role_class)

def set_patient_primary_chw(django_patient, django_actor):
    """
    Add an actor as an exteranl provider for the given patient.
    """
    role_class = Role.objects.get(name=constants.role_primary_chw)
    permissions.utils.add_local_role(django_patient, django_actor, role_class)

def add_external_provider_to_patient(django_patient, django_actor):
    """
    Add an actor as an exteranl provider for the given patient.
    """
    role_class = Role.objects.get(name=constants.role_external_provider)
    permissions.utils.add_role(django_actor, role_class)
    permissions.utils.add_local_role(django_patient, django_actor, role_class)


def get_permissions(actor_doc, direct=False):
    djactor = actor_doc.django_actor
    if direct:
        direct_permissions = PrincipalRoleRelation.objects.filter(actor=djactor).exclude(content_id=None)
        return direct_permissions
    else:
        return PrincipalRoleRelation.objects.filter(actor=djactor)


def get_permissions_dict(actor_doc, direct=False):
    perms = get_permissions(actor_doc, direct=direct)
    ret = {}
    for p in perms:
        arr = ret.get(p.role, [])
        arr.append(p.content)
        ret[p.role] = arr
    return ret


def get_careteam(patient):
    #django patient
    direct_permissions = PrincipalRoleRelation.objects.filter(content_type=ContentType.objects.get_for_model(patient), content_id=patient.id)
    return direct_permissions


def get_chw(chw_doc_id):
    """
    check other permissions?
    """
    return CHWActor.get(chw_doc_id)

def get_chws():
    """
    Returns actor documents of external providers in the system
    """
    chw_role = Role.objects.get(name=constants.role_chw)
    django_provider_actors = PrincipalRoleRelation.objects.filter(role=chw_role).filter(content_id=None)
    actor_doc_ids = django_provider_actors.distinct().values_list('actor__doc_id', flat=True)
    actor_docs = ProviderActor.view('actorpermission/all_actors', keys=list(actor_doc_ids), include_docs=True).all()
    return actor_docs

