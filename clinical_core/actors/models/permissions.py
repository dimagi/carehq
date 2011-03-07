from dimagi.utils import make_uuid
from django.db import models

class RoleIdentityManager(models.Manager):
    def for_user(self, user):
        """
        Returns all actor objects for a given user
        """
        return super(RoleIdentityManager, self).get_query_set().filter(user=user)
    def is_provider(self, user):
        """
        Coarse level permission/role for user object
        """
        triage_type= ContentType.objects.get_for_model(TriageNurse)
        doc_type = ContentType.objects.get_for_model(Doctor)
        q_doctype = Q(role_type=doc_type)
        q_triagetype = Q(role_type=triage_type)
        q_user = Q(user=user)
        
        return super(RoleIdentityManager, self).get_query_set().filter(q_user, q_doctype | q_triagetype)
    def is_caregiver(self, user):
        """
        Coarse level permission/role for user object
        """
        caregiver_type = ContentType.objects.get_for_model(Caregiver)
        q_caregiver_type = Q(role_type=caregiver_type)
        q_user = Q(user=user)
        return super(RoleIdentityManager, self).get_query_set().filter(q_user, q_caregiver_type)

    def create_role(self, role):
        """
        Helper function to create actors
        """
        #sanity check to see if it exists already
        exists_qset = super(RoleIdentityManager, self).get_query_set().filter(role=role)
        if exists_qset.count() > 0:
            raise Exception("Error, attempting to create an actor that otherwise already exists")
        else:
            instance = self.model(role=role)
            instance.save()
            return instance




class RolePermissionManager(models.Manager):
    def get_roles(self, patient, user):
        """
        For a given patient, and a given login, this is a challenge to verify that the user has a role.
        Returns a Queryset of the roles that the user has for the given patient.
        """
        ptlinks = PatientLink.objects.filter(patient=patient, role__user=user, active=True)
        #ok, so we have the PatienLinks
        roles = ptlinks.values_list('role__id', flat=True)
        return Role.objects.all().filter(id__in=roles)

    def for_patient(self, patient):
        """
        Manager method to return actors for a given patient
        """
        return Actor.objects.filter(id__in=PatientLink.objects.filter(patient=patient).values_list('actor__id', flat=True))
    
    def get_patients(self):
        """
        For this actor, return if this actor has patients under its care.
        """
        pals = PatientLink.objects.filter(actor=self).values_list('patient__id', flat=True)
        return Patient.objects.filter(id__in=pals)
    
#    def get_providers(self, patient):
#        """
#        Return a queryset of Actors that have the role of a provider
#        """
#        triage_type= ContentType.objects.get_for_model(TriageNurse)
#        doc_type = ContentType.objects.get_for_model(Doctor)
#        q_doctype = Q(role__role_type=doc_type)
#        q_triagetype = Q(role__role_type=triage_type)
#        return Actor.objects.filter(id__in=PatientLink.objects.filter(q_doctype | q_triagetype).values_list('actor__id', flat=True))
#
#    def get_caregivers(self, patient):
#        """
#        Return a queryset of Actors that have the role of a caregiver
#        """
#        caregiver_type = ContentType.objects.get_for_model(Caregiver)
#        q_caregiver_type = Q(role__role_type=caregiver_type)
#        return Actor.objects.filter(PatientLink.objects.filter(q_caregiver_type).values_list('actor__id', flat=True))
#
    def can_view(self, patient, user):
        if patient.user == user:
            #sanity check to see if the patient IS the user (duh)
            return True

        triage_type= ContentType.objects.get_for_model(TriageNurse)
        doc_type = ContentType.objects.get_for_model(Doctor)
        q_doctype = Q(role_type=doc_type)
        q_triagetype = Q(role_type=triage_type)

        caregiver_type = ContentType.objects.get_for_model(Caregiver)
        q_caregiver_type = Q(role__role_type=caregiver_type)

        q_actor_query = Q(role__user=user)
        q_patient = Q(patient=patient)
        
        links = PatientLink.objects.filter(q_actor_query, q_patient)
        if links.count() > 0:
            return True
        else:
            return False
        
        


    