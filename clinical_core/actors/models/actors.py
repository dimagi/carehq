from roles import *


class ActorManager(models.Manager):
    def for_user(self, user):
        """
        Returns all actor objects for a given user
        """
        return super(ActorManager, self).get_query_set().filter(role__user=user)
    def is_provider(self, user):
        """
        Coarse level permission/role for user object
        """
        triage_type= ContentType.objects.get_for_model(TriageNurse)
        doc_type = ContentType.objects.get_for_model(Doctor)
        q_doctype = Q(role__role_type=doc_type)
        q_triagetype = Q(role__role_type=triage_type)        
        q_user = Q(role__user=user)
        
        return super(ActorManager, self).get_query_set().filter(q_user, q_doctype | q_triagetype)    
    def is_caregiver(self, user):
        """
        Coarse level permission/role for user object
        """
        caregiver_type = ContentType.objects.get_for_model(Caregiver)
        q_caregiver_type = Q(role__role_type=caregiver_type)
        q_user = Q(role__user=user)
        return super(ActorManager, self).get_query_set().filter(q_user, q_caregiver_type)

    def create_actor(self, role):
        """
        Helper function to create actors
        """
        #sanity check to see if it exists already
        exists_qset = super(ActorManager, self).get_query_set().filter(role=role)
        if exists_qset.count() > 0:
            raise Exception("Error, attempting to create an actor that otherwise already exists")
        else:
            instance = self.model(role=role)
            instance.save()
            return instance




class ActorPermissionManager(models.Manager):
    def get_roles(self, patient, user):
        """
        For a given patient, and a given login, this is a challenge to verify that the user has a role.
        Returns a Queryset of the roles that the user has for the given patient.
        """
        ptlinks = PatientActorLink.objects.filter(patient=patient, actor__role__user=user, active=True)
        #ok, so we have the PatientActorLinks
        roles = ptlinks.values_list('actor__role__id', flat=True)
        return Role.objects.all().filter(id__in=roles)

    def for_patient(self, patient):
        """
        Manager method to return actors for a given patient
        """
        return Actor.objects.filter(id__in=PatientActorLink.objects.filter(patient=patient).values_list('actor__id', flat=True))
    
    def get_patients(self):
        """
        For this actor, return if this actor has patients under its care.
        """
        pals = PatientActorLink.objects.filter(actor=self).values_list('patient__id', flat=True)
        return Patient.objects.filter(id__in=pals)
    
#    def get_providers(self, patient):
#        """
#        Return a queryset of Actors that have the role of a provider
#        """
#        triage_type= ContentType.objects.get_for_model(TriageNurse)
#        doc_type = ContentType.objects.get_for_model(Doctor)
#        q_doctype = Q(actor__role__role_type=doc_type)
#        q_triagetype = Q(actor__role__role_type=triage_type)
#        return Actor.objects.filter(id__in=PatientActorLink.objects.filter(q_doctype | q_triagetype).values_list('actor__id', flat=True))
#
#    def get_caregivers(self, patient):
#        """
#        Return a queryset of Actors that have the role of a caregiver
#        """
#        caregiver_type = ContentType.objects.get_for_model(Caregiver)
#        q_caregiver_type = Q(actor__role__role_type=caregiver_type)
#        return Actor.objects.filter(PatientActorLink.objects.filter(q_caregiver_type).values_list('actor__id', flat=True))
#
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

        q_actor_query = Q(actor__role__user=user)
        q_patient = Q(patient=patient)
        
        links = PatientActorLink.objects.filter(q_actor_query, q_patient)
        if links.count() > 0:
            return True
        else:
            return False
        
        
class Actor(models.Model):
    """
    The Actor is the primary way in which an authenticated User gets mapped to a particular role and permission through the system.     
    """    
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)    
    role = models.ForeignKey(Role, unique=True) #Multiple roles, multiple actors.  this essentially makes it a 1:1 mapping of actors to roles.  Revocation of actor access is done at the actor level, retaining the Role instance.

    objects = ActorManager()
    permissions = ActorPermissionManager()

    @property
    def user(self):
        return self.role.user

    @property
    def patients(self):
        """
        Property that retuns queryset of patients that this actor can view.
        Was originally a many to many through, but it now needs to be explicitly defined.
        """
        link_patient_ids = PatientActorLink.objects.filter(actor=self).values_list('patient__id', flat=True)
        return Patient.objects.filter(id__in=link_patient_ids)
    
    def __unicode__(self):
        return "Actor [%s] is a %s" % (self.role.description, self.role)

    @property
    def title(self):
        return self.role.description

    class Meta:
        app_label = 'actors'
        verbose_name = "Actor"
        verbose_name_plural = "Actors"        


class PatientActorLink(models.Model):
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    patient = models.ForeignKey(Patient)
    actor = models.ForeignKey(Actor)
    
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=make_time)
    modified_date = models.DateTimeField(default=make_time)    
    
    class Meta:
        app_label = 'actors'
        unique_together = ('patient','actor')
    
    def __unicode__(self):
        return "Patient(%s) :: %s" % (self.patient, self.actor)



##################
##bootstrap code to be run at startup
#for cls in Role.__subclasses__():             
#    ctype = ContentType.objects.get_for_model(cls)
#    model = ctype.model_class()


    