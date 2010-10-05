from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from clinical_core.patient.models import Patient
from django.db.models import Q

from clincore.utils import make_uuid, make_time

class Role(models.Model):
    """
    A role is a base class for defining some type of affiliation/description of an individual in the system.
    A role by itself is actually quite meaningless in what data it contains.
    
    The instance of the role acts as a differentiator to aide in querying permissions.
    The data contained within the role instance itself *should be specific* to the role  you're creating for a given user.
    The role you define *will* be bound via the Actor object to the user you want to create an actor for.  Be specific!
    
    Roles 
    """
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    
    role_type = models.ForeignKey(ContentType, verbose_name='Role Subclass Content Type', blank=True, null=True)
    role_uuid = models.CharField('role_uuid', max_length=32, db_index=True, blank=True, null=True)
    role_object = generic.GenericForeignKey('role_type', 'role_uuid')    
    
    def save(self):
        #self.id = uuid.uuid1().hex
        self.role_type = self.child_contenttype()        
        self.role_uuid = self.id
        super(Role, self).save()


    class Meta:
        app_label = 'actors'
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        unique_together = ('role_type', 'role_uuid')
    
    @classmethod
    def child_contenttype(cls):
        ct = ContentType.objects.get(model=cls.__name__.lower())
        return ct
    
    def __unicode__(self):
        return "Role Base: %s: %s" % (self.role_type, self.role_object)    

class CHW(Role):
    title = models.CharField(max_length=64)
    specialty = models.CharField(max_length=64)

    class Meta:
        app_label = 'actors'
        verbose_name = "Role (CHW)"
        verbose_name_plural = "Roles (CHW)"

    def __unicode__(self):
        return "CHW: %s at %s" % (self.title, self.specialty)
    
class TriageNurse(Role):
    title = models.CharField(max_length=64)
    department= models.CharField(max_length=64)

    class Meta:
        app_label = 'actors'
        verbose_name = "Role (Triage Nurse)"
        verbose_name_plural = "Roles (Triage Nurse)"

    def __unicode__(self):
        return "TriageNurse: %s at %s" % (self.title, self.department)


PROVIDER_ROLE_CHOICES = (
                  ('oncologist', 'Oncologist'),
                  ('pcp', 'Primary Care Physician'),
                  ('socialworker', 'Social Worker'),
                  ('other-doctor', 'Other Doctor'),
                  ('other-nurse', 'Other Nurse'),
                  ('nurse', 'Nurse'),
                  ('nurse-triage', 'Triage Nurse'),
                  ('lab', 'Laboratory'),
                  ('other', 'Other'),
                  )


class Doctor(Role):
    title = models.CharField(max_length=64)
    department = models.CharField(max_length=64)
    specialty = models.CharField(max_length=64)

    class Meta:
        app_label = 'actors'
        verbose_name = "Role (Doctor)"
        verbose_name_plural = "Roles (Doctor)"
    
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

    class Meta:
        app_label = 'actors'
        verbose_name = "Role (Caregiver)"
        verbose_name_plural = "Roles (Caregiver)"

    def __unicode__(self):
        return "Caregiver: %s" % (self.get_relationship_type_display())
