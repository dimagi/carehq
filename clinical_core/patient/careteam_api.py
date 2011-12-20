
#NOTE FOR ALL FUTURE GENERATIONS
#All API calls must use the doc_id, NOT the django ID.  The doc_id is sacrosanct.


#api functions to abstract the underlying permissions
from django.contrib.contenttypes.models import ContentType
import permissions
from permissions.models import PrincipalRoleRelation

def add_to_careteam(patient, actor, role):
    """
    For a given django patient and django actor, assign the given role
    """
    permissions.utils.add_local_role(patient.django_patient, actor.django_actor, role)

def remove_from_careteam(patient, actor):
    pass


def change_role(patient, actor, role):
    pass

def get_role(patient, actor):
    pass


def has_permission(patient, actor, permission):
    pass

def get_careteam(django_patient, omit_patient=True):
    """
    Do query on PrincipalRoleRelation to find principals (actors) with local relationships with the given patient django document
    Return a dictionary keyed by the role, of actor arrays - django actors.
    """
    ctype = ContentType.objects.get_for_model(django_patient)
    proles = PrincipalRoleRelation.objects.filter(content_type=ctype, content_id=django_patient.id)

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


#can see?
#can edit?