from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from clinical_core.patient.models import Patient
from datetime import datetime
from django.utils.functional import curry
from django.db.models import Q

import uuid

def make_time():
    return datetime.utcnow()

def make_uuid():
    return uuid.uuid1().hex

class RoleManager(models.Manager):
    pass
    
     

class Role(models.Model):
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    
    role_type = models.ForeignKey(ContentType, verbose_name='Role Subclass Content Type', blank=True, null=True)
    role_uuid = models.CharField('role_uuid', max_length=32, db_index=True, blank=True, null=True)
    role_object = generic.GenericForeignKey('role_type', 'role_uuid')    
    
    objects = RoleManager()
#    @classmethod
#    def create_role
    
    def save(self):
        #self.id = uuid.uuid1().hex
        self.role_type = self.child_contenttype()        
        self.role_uuid = self.id
        super(Role, self).save()

    
    @classmethod
    def child_contenttype(cls):
        ct = ContentType.objects.get(model=cls.__name__.lower())
        return ct
    
    def __unicode__(self):
        return "Role Base: %s: %s" % (self.role_type, self.role_object)    
    
class TriageNurse(Role):
    title = models.CharField(max_length=64)
    department= models.CharField(max_length=64)
    
    def __unicode__(self):
        return "TriageNurse: %s at %s" % (self.title, self.department)
    
class Doctor(Role):
    title = models.CharField(max_length=64)
    department = models.CharField(max_length=64)
    specialty = models.CharField(max_length=64)
    
    def __unicode__(self):
        return "Doctor: %s - %s at %s" % (self.title, self.specialty, self.department)
    
    
    
    
class Caregiver(Role):    
    RELATIONSHIP_CHOICES = (
                      ('guardian', 'Guardian'),
                      ('child', 'Child'),
                      ('parent', 'Parent'),
                      ('relative', 'Relative'),
                      ('spouse', 'Spouse'),
                      ('nextofkin', 'Next of kin'),
                      ('friend', 'Friend'),
                      ('neighbor', 'Neighbor'),
                      ('other', 'Other'),
    )
    relationship_type = models.CharField(choices=RELATIONSHIP_CHOICES,max_length=32)
    notes = models.CharField(max_length=512, null=True, blank=True)

    def __unicode__(self):
        return "Caregiver: %s" % (self.get_relationship_type_display())
    

class ActorManager(models.Manager):
    def for_user(self, user):
        """
        Returns all actor objects for a given user
        """
        return super(ActorManager, self).get_query_set().filter(user=user)
    def is_provider(self, user):
        """
        Coarse level permission/role for user object
        """
        triage_type= ContentType.objects.get_for_model(TriageNurse)
        doc_type = ContentType.objects.get_for_model(Doctor)
        q_doctype = Q(role__role_type=doc_type)
        q_triagetype = Q(role__role_type=triage_type)        
        q_user = Q(user=user)
        
        return super(ActorManager, self).get_query_set().filter(q_user, q_doctype | q_triagetype)
    
    
    def is_caregiver(self, user):
        """
        Coarse level permission/role for user object
        """
        caregiver_type = ContentType.objects.get_for_model(Caregiver)
        q_caregiver_type = Q(role__role_type=caregiver_type)
        q_user = Q(user=user)                    
        return super(ActorManager, self).get_query_set().filter(q_user, q_caregiver_type)    

class ActorPatientManager(models.Manager):

    def get_roles(self, patient, user):
        """
        For a given patient, and a given login, this is a challenge to verify that the user has a role.
        Returns a Queryset of the roles that the user has for the given patient.
        """
        ptlinks = PatientActorLink.objects.filter(patient=patient, actor__user=user, active=True)
        #ok, so we have the PatientActorLinks
        roles = ptlinks.values_list('actor__role__id', flat=True)
        print roles
        return Role.objects.all().filter(id__in=roles)


    def for_patient(self, patient):
        """
        Manager method to return actors for a given patient
        """
        return Actor.objects.filter(id__in=PatientActorLink.objects.filter(patient=patient).values_list('actor__id', flat=True))
    
    def get_providers(self, patient):
        """
        Return a queryset of Actors that have the role of a provider
        """
        triage_type= ContentType.objects.get_for_model(TriageNurse)
        doc_type = ContentType.objects.get_for_model(Doctor)
        q_doctype = Q(actor__role__role_type=doc_type)
        q_triagetype = Q(actor__role__role_type=triage_type)        
        return Actor.objects.filter(id__in=PatientActorLink.objects.filter(q_doctype | q_triagetype).values_list('actor__id', flat=True))
    
    def get_caregivers(self, patient):
        """
        Return a queryset of Actors that have the role of a caregiver
        """
        caregiver_type = ContentType.objects.get_for_model(Caregiver)
        q_caregiver_type = Q(actor__role__role_type=caregiver_type)        
        return Actor.objects.filter(PatientActorLink.objects.filter(q_caregiver_type).values_list('actor__id', flat=True))
    
    def can_view(self, patient, user):
        if patient.user == user:
            #sanity check to see if the patient IS the user (duh)
            return True

        triage_type= ContentType.objects.get_for_model(TriageNurse)
        doc_type = ContentType.objects.get_for_model(Doctor)
        q_doctype = Q(actor__role__role_type=doc_type)
        q_triagetype = Q(actor__role__role_type=triage_type)

        caregiver_type = ContentType.objects.get_for_model(Caregiver)
        q_caregiver_type = Q(actor__role__role_type=caregiver_type)        
        
        q_actor_query = Q(actor__user=user)
        q_patient = Q(patient=patient)
        
        links = PatientActorLink.objects.filter(q_actor_query, q_patient)
        if links.count() > 0:
        #    pals = PatientActorLink.objects.all().filter(actor__user=user)
            return True
        else:
            return False
        
        
class Actor(models.Model):
    """
    The Actor is the primary way in which an authenticated User gets mapped to a particular role and permission through the system.     
    """    
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)    
    role = models.ForeignKey(Role)
    user = models.ForeignKey(User, blank=True, null=True, related_name='actors') #nullable because the actor need not be a user, could be a background process
    patients = models.ManyToManyField(Patient, through='PatientActorLink')
    
    objects = ActorManager()
    patient_objects = ActorPatientManager()
    
    def __unicode__(self):
        return "Actor [%s] is a %s" % (self.user, self.role)

    class Meta:
        verbose_name = "Actor"
        verbose_name_plural = "Actors"        
        unique_together = ('user', 'role')


class PatientActorLink(models.Model):
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    patient = models.ForeignKey(Patient)
    actor = models.ForeignKey(Actor)
    
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=make_time)
    modified_date = models.DateTimeField(default=make_time)    
    
    class Meta:
        unique_together = ('patient','actor')
    
    def __unicode__(self):
        return "Patient(%s) :: %s" % (self.patient, self.actor)
#    
#    
#    
##################
##bootstrap code to be run at startup
#for cls in Role.__subclasses__():             
#    ctype = ContentType.objects.get_for_model(cls)
#    model = ctype.model_class()


    