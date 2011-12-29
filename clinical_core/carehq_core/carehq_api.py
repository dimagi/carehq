from django.contrib.contenttypes.models import ContentType
from django.db.models.query_utils import Q
from actorpermission.models.actortypes import ProviderActor, CHWActor
from carehq_core import carehq_constants
import permissions
from permissions.models import Role, PrincipalRoleRelation


def add_to_careteam(patient_doc, actor_doc, role):
    """
    For a given django patient and django actor, assign the given role
    """
    permissions.utils.add_local_role(patient_doc.django_patient, actor_doc.django_actor, role)

def get_external_providers():
    """
    Returns actor documents of external providers in the system
    """
    provider_role = Role.objects.get(name=carehq_constants.role_external_provider)
    django_provider_actors = PrincipalRoleRelation.objects.filter(role=provider_role).filter(content_id=None)
    actor_doc_ids = django_provider_actors.distinct().values_list('actor__doc_id', flat=True)
    actor_docs = ProviderActor.view('actorpermission/all_actors', keys=list(actor_doc_ids), include_docs=True).all()
    return actor_docs


def add_chw(chw_actor):
    """
    For a given actor document, give it a global role of CHW.
    """

    role_class = Role.objects.get(name=carehq_constants.role_chw)
    return permissions.utils.add_role(chw_actor.django_actor, role_class)

def add_provider(actor_doc):
    role_class = Role.objects.get(name=carehq_constants.role_provider)
    return permissions.utils.add_role(actor_doc.django_actor, role_class)



def set_patient_primary_chw(patient_doc, actor_doc):
    """
    Add an actor as an exteranl provider for the given patient.
    """

    role_class = Role.objects.get(name=carehq_constants.role_primary_chw)
    permissions.utils.add_local_role(patient_doc.django_patient, actor_doc.django_actor, role_class)

def add_external_provider_to_patient(patient_doc, actor_doc):
    """
    Add an actor as an exteranl provider for the given patient.
    """

    role_class = Role.objects.get(name=carehq_constants.role_external_provider)
    permissions.utils.add_role(actor_doc.django_actor, role_class)
    permissions.utils.add_local_role(patient_doc.django_patient, actor_doc.django_actor, role_class)


def get_permissions(actor_doc, direct=False):
    djactor = actor_doc.django_actor
    if direct:
        direct_permissions = PrincipalRoleRelation.objects.filter(actor=djactor).exclude(content_id=None)
        return direct_permissions
    else:
        return PrincipalRoleRelation.objects.filter(actor=djactor)


def get_permissions_dict(actor_doc, direct=False):
    """
    Return a dictionary of permissions for this given actor
    {role: [principalrolerelation, ... ],  }
    """
    perms = get_permissions(actor_doc, direct=direct)
    ret = {}
    for p in perms:
        arr = ret.get(p.role, [])
        arr.append(p.content)
        ret[p.role] = arr
    return ret


def get_patient_providers(patient_doc):
    all_prrs = get_careteam(patient_doc)
    q_providers = Q(role__name=Role.objects.get(name=carehq_constants.role_provider))
    q_primary_providers = Q(role__name=Role.objects.get(name=carehq_constants.role_primary_provider))
    q_external_providers = Q(role__name=Role.objects.get(name=carehq_constants.role_external_provider))
    provider_prrs = all_prrs.filter(q_providers | q_external_providers | q_primary_providers)
    return provider_prrs

def get_patient_caregivers(patient_doc):
    all_prrs = get_careteam(patient_doc)
    q_caregivers = Q(role__name=Role.objects.get(name=carehq_constants.role_caregiver))
    caregiver_prrs = all_prrs.filter(q_caregivers)
    return caregiver_prrs

def get_careteam(patient_doc):
    """
    Get the careteam queryset for a given patient document.
    """
    #django patient
    direct_permissions = PrincipalRoleRelation.objects.filter(content_type=ContentType.objects.get_for_model(patient_doc.django_patient), content_id=patient_doc.django_uuid)
    return direct_permissions

def get_careteam_dict(patient_doc, omit_patient=True):
    """
    Do query on PrincipalRoleRelation to find principals (actors) with local relationships with the given patient django document
    Return a dictionary keyed by the role, of actor arrays - django actors.
    """
    ctype = ContentType.objects.get_for_model(patient_doc.django_patient)
    proles = PrincipalRoleRelation.objects.filter(content_type=ctype, content_id=patient_doc.django_patient.id)

    if omit_patient:
        #total hack yo
        proles = proles.exclude(role__display="Patient")

#    d = dict((k,v) for (k,v) in blah blah blah)
    role_actor_dict = {}
    for pr in proles:
        actors = role_actor_dict.get(pr.role, [])
        if pr.actor not in actors:
            actors.append(pr.actor)
        role_actor_dict[pr.role] = actors
    return role_actor_dict


def get_chw(chw_doc_id):
    """
    check other permissions?
    """
    return CHWActor.get(chw_doc_id)

def get_chws():
    """
    Returns actor documents of external providers in the system
    """
    chw_role = Role.objects.get(name=carehq_constants.role_chw)
    django_provider_actors = PrincipalRoleRelation.objects.filter(role=chw_role).filter(content_id=None)
    actor_doc_ids = django_provider_actors.distinct().values_list('actor__doc_id', flat=True)
    actor_docs = CHWActor.view('actorpermission/all_actors', keys=list(actor_doc_ids), include_docs=True).all()
    return actor_docs

